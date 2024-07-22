__author__ = 'bittremieux, walzer'
import json
import mzqc
import os
import urllib.request
from typing import Dict, List, Set, Union, Tuple, Any
from mzqc.MZQCFile import MzQcFile, BaseQuality, RunQuality, SetQuality, QualityMetric, MetaDataParameters, CvParameter
from itertools import chain
from dataclasses import dataclass, field
from collections import UserDict

import jsonschema
from pronto import Ontology, Term
from contextlib import contextmanager
import os
import sys
from jsonschema.exceptions import ValidationError

@contextmanager
def suppress_verbose_modules():
    with open(os.devnull, "w") as devnull:
        sys_stderr_bak = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stderr = sys_stderr_bak

@dataclass
class SemanticIssue:
    """Class for keeping track of an instance of all the different issues during the 
        semantic validation for a particular dataset, collecting a few data members:
        name: name of the issue
        severity: value from 1-9, increasing severity, no checks performed, no guaranties.
        message: issue message
    Added is a _to_string function to simplify serialisation.
    Note: ValidationError was too inflexible for development, hence the dataclass.
    """
    name: str
    severity: int
    message: str
    def _to_string(self):
        return self.name + " of severity "+ str(self.severity) + " and message: " + self.message

class SemanticCheck(UserDict):
    """Class for keeping track of all instances of SemanticIssues arising during semantic validation.
    
    Due to the design and nature of checks performed, it is recommended to use one object per 
    loaded mzQC file. Thus, if you provide the file_path of a loaded mzQC object to the 
    SemanticCheck class, you can directly document to which file (and not only which object) the 
    validation belongs to. The validation results are directly accessible through the UserDict 
    super class. Additional parameters on the validation call are kept, too. 
    The validate function updates internal data attributes as max_error, the dict of 
    SemanticIssues, and the mzqc_obj (see __init__). A wrapping function to add new-found 
    validation issues with raising() helps keeping track of the number of issues during validation,
    which can be cut short in resource restrictive environments.
    Like so, the class objects can perform different modes of validation on the same mzqc. However,
    this makes the SemanticCheck object memory heavy. The class uses a number of internal functions
    to capsulate the validation process and access to the mzqc_object: `clear`, `raising`, and 
    `string_export` which are present as convenience functions to the validator applications in the
    accessories of the project's repository. See the `validate` function documentation for further 
    details. 
    
    Parameters
    ----------
    UserDict : Dict[str,List[SemanticIssue]]
        keeps track of the issues during validation
    """
    def __init__(self, mzqc_obj: MzQcFile, version: str="", file_path: str=""):
        super().__init__()
        self.version = version
        self.file_path = file_path
        self.mzqc_obj = mzqc_obj
        # the following are to keep record of the validation parameters and set by the validate() function
        self._max_errors:int=0
        self._load_local:bool=False
        self._keep_issues:bool=False
        self._exceeded_errors:bool=False

    def __setitem__(self, key, value):
        """Overrides the UserDict item to keep watch on the maximum allowed number of 
        registered issues before validation is interrupted (through an error raised from
        this function)

        Parameters
        ----------
        key : str
            issue type or category
        value : list[SemanticIssues]
            the list of SemanticIssues found for given category

        Raises
        ------
        ValidationError
            if self._max_errors is exceeded by the sum of items contained in category lists of issues
        """
        if self._max_errors > 0:
            if sum([len(x) for x in self.values()])+1 > self._max_errors:
                self._exceeded_errors = True
                super().__setitem__(key, value)
                super().__setitem__("general", [SemanticIssue("Max semantic issues", 1,
                                f"Maximum number of semantic errors incurred ({self._max_errors} < {sum([len(x) for x in self.values()])}), aborting!")])
                raise ValidationError("Maximum number of semantic errors incurred ({me} < {ie}), aborting!".format(
                    ie=sum([len(x) for x in self.values()]), me = self._max_errors))
        super().__setitem__(key, value)
    
    def raising(self, category:str, issue:SemanticIssue):
        """Helper function to append new issues without circumventing the max_error 
        mechanism or initialising new issue types or categories

        Parameters
        ----------
        category : str
            issue type or category, key to __setitem__
        issue : SemanticIssue
            A 
        """
        if category not in self.keys():
            self[category]=[issue]
        else:
            self[category]=self[category]+[issue]

    def clear(self) -> None:
        """Substitute to the UserDict clear which clears the dict and resets _exceeded_errors
        """
        super().clear() 
        self._exceeded_errors = False
        return

    def _get_cv_parameters(self, val: object):
        """Recursively retrieves all elements of type cvParameter from the object

        Parameters
        ----------  
        val : object
            a nested object (list or mzQC)

        Yields
        ------
        cvParameter
            any object that has an 'accession' member
        """
        if hasattr(val, 'accession'):
            yield val
        elif isinstance(val, List):
            for v in val:
                yield from self._get_cv_parameters(v)
        elif isinstance(val, (MzQcFile,SetQuality,RunQuality,MetaDataParameters)):
            for attr, value in vars(val).items():
                yield from self._get_cv_parameters(value)
        else:
            # recursion dead-end
            pass

    def _check_label_uniqueness(self, issue_type_category: str, _document_collected_issues: bool = False):
        """Checks a mzQC object's metadata labels for uniqueness

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed
        _document_collected_issues : bool, optional
            for auto documentation this is set True, by default False
        """
        if _document_collected_issues:
            self.raising(issue_type_category, SemanticIssue("Metadata labels", 6,
                    "Run/SetQuality label {} is not unique in file!".format("auto_doc")))
            return        
        
        uniq_labels = set()
        for qle in chain(self.mzqc_obj.runQualities,self.mzqc_obj.setQualities):
            if qle.metadata.label in uniq_labels:
                self.raising(issue_type_category, SemanticIssue("Metadata labels", 6,
                    "Run/SetQuality label {} is not unique in file!".format(qle.metadata.label)))
            else: 
                uniq_labels.add(qle.metadata.label)

        return
    
    def _load_and_check_Vocabularies(self, issue_type_category: str, load_local: bool = False, _document_collected_issues: bool = False) -> Dict[str,Ontology]:
        """Loads remote or local vocabularies and registers any issues during load

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed 
        load_local : bool, optional
            if True file URIs referencing a local fs are attempted to load, by default False
        _document_collected_issues : bool, optional
            for auto documentation this is set True, by default False

        Returns
        -------
        Dict[str,Ontology]
            the loaded vocabularies as pronto Ontlogies, key is the name of the Ontology
        """
        if _document_collected_issues:
            self.raising(issue_type_category, SemanticIssue("Loading local vocabulary", 5, 
                    f'Loading the following local ontology referenced in mzQC file: {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Loading online vocabulary", 5, 
                    f'Error loading the following online ontology referenced in mzQC file: {"auto_doc"}'))         
            return
        
        vocs = dict()

        # check if ontologies are listed multiple times (different versions etc)
        for cve in self.mzqc_obj.controlledVocabularies:
            try:
                # check if local CV was used
                if load_local:
                    loc = cve.uri
                    if loc.startswith('file://'):
                        loc = loc[len('file://'):]
                        self.raising(issue_type_category, SemanticIssue("Loading local vocabulary", 5, 
                                                  f'Loading the following local ontology referenced in mzQC file: {loc}'))
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(loc, import_depth=0)
                else:
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(cve.uri, import_depth=0)
            except Exception as e:
                self.raising(issue_type_category, SemanticIssue("Loading online vocabulary", 5, 
                                          f'Error loading the following online ontology referenced in mzQC file: {e}'))
        return vocs

    def _check_InputFile_consistency(self, issue_type_category: str, _document_collected_issues: bool = False):
        """Checks the InputFile consistency of given mzqc_object

        The mzqc_object is read from self, and issues detected will be appended
        to self inside the given category. In case _document_collected_issues 
        evaluates to True, the actual checks are skipped and all possible 
        issues auto-generated.

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed 
        _document_collected_issues : bool
            for auto documentation this is set True, by default False
        """
        if _document_collected_issues:
            self.raising(issue_type_category, 
                         SemanticIssue("Inconsistent input file", 4,
                                        f'Inconsistent file name and location: '
                                        f'{"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Reused file location", 6,
                                        f'Duplicate inputFile locations within '
                                        f'a metadata object: '
                                        f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Duplicate input files", 5,
                                        f'Duplicate input files in a run/set: '
                                        f'accession = {"auto_doc"}'))
            return
        
        input_file_sets = list()
        for quality in chain(self.mzqc_obj.runQualities, self.mzqc_obj.setQualities):
            one_input_file_set = set()
            for input_file in quality.metadata.inputFiles:
                # filename and location
                infilo = os.path.splitext(
                    os.path.basename(input_file.location))[0]
                if input_file.name != infilo:
                    self.raising(issue_type_category, 
                                 SemanticIssue("Inconsistent input file", 4,
                                                f'Inconsistent file name and location:'
                                                f'{input_file.name}/{infilo}'))
                one_input_file_set.add(input_file.location)

            # if more than 2 inputs but just one location
            if len(quality.metadata.inputFiles) != len(one_input_file_set):
                self.raising(issue_type_category, 
                             SemanticIssue("Reused file location", 6,
                                            f'Duplicate inputFile locations within '
                                            f'a metadata object: '
                                            f'accession = {one_input_file_set}'))

            # check duplicates 
            if one_input_file_set in input_file_sets:
                    self.raising(issue_type_category, 
                                 SemanticIssue("Duplicate input files", 5,
                                                f'Duplicate input files in a run/set: '
                                                f'accession = {one_input_file_set}'))
            else:
                input_file_sets.append(one_input_file_set)
        return

    def _getVocabularyMetrics(self, filevocabularies: Dict[str,Ontology]) -> Set[str]:
        """Retrieves all metric type accessions from given vocabularies

        Parameters
        ----------
        filevocabularies : Dict[str,Ontology]
            the vocabularies given as a dict of names and pronto Ontology objects

        Returns
        -------
        Set[str]
            a set of accessions of metric type terms in the given vocabularies
        """
        metricsubclass_sets_list = list()
        for k,v in filevocabularies.items():
            try:
                metricsubclass_sets_list.append({x.id for x in v['MS:4000002'].subclasses().to_set()})
            except KeyError:
                pass
        return set().union(chain.from_iterable(metricsubclass_sets_list))

    def _getVocabularyIDMetrics(self, filevocabularies: Dict[str,Ontology]) -> Set[str]:
        """Retrieves all ID based type accessions from given vocabularies

        Parameters
        ----------
        filevocabularies : Dict[str,Ontology]
            the vocabularies given as a dict of names and pronto Ontology objects

        Returns
        -------
        Set[str]
            a set of accessions of ID based type terms in the given vocabularies
        """
        metricsubclass_sets_list = list()
        for k,v in filevocabularies.items():
            try:
                metricsubclass_sets_list.append(
                    {pib.id for pib in {x for x in v['MS:4000002'].subclasses().to_set()} if \
                     v['MS:4000008'] in pib.relationships.get(v.get_relationship('has_metric_category'),[])}\
                )
            except KeyError:
                pass
        return set().union(chain.from_iterable(metricsubclass_sets_list))

    def _getVocabularyTables(self, filevocabularies: Dict[str,Ontology]) -> Set[str]:
        """Retrieves all table type accessions from given vocabularies

        Parameters
        ----------
        filevocabularies : Dict[str,Ontology]
            the vocabularies given as a dict of names and pronto Ontology objects

        Returns
        -------
        Set[str]
            a set of accessions of table type terms in the given vocabularies
        """
        tablesubclass_sets_list = list()
        for k,v in filevocabularies.items():
            try:
                tablesubclass_sets_list.append({x.id for x in v['MS:4000005'].subclasses().to_set()})
            except KeyError:
                pass
        return set().union(chain.from_iterable(tablesubclass_sets_list))

    def _getRequiredCols(self, accession: str, filevocabularies: Dict[str,Ontology]) -> Tuple[Set[Term],Set[Term]]:
        """Retrieves the names of required columns from the given accession

        The accession is looked up in the given vocabularies

        Parameters
        ----------
        accession : str
            accession of a table type metric within the given vocabularies
        filevocabularies : Dict[str,Ontology]
            the vocabularies given as a dict of names and pronto Ontology objects

        Returns
        -------
        Tuple[Set[Term],Set[Term]]
            a tuple of sets, the first for required columns' names,  the second for the optional columns' names 
        """
        tab_def = None
        for k,v in filevocabularies.items():
            try:
                tab_def = v[accession]
                break
            except KeyError:
                pass
        if not tab_def:
            return set(),set()
        else:
            return set(next(filter(lambda x: x[0].name=='has_column', tab_def.relationships.items()), (None,frozenset()))[1]), set(next(filter(lambda x: x[0].name=='has_optional_column', tab_def.relationships.items()), (None,frozenset()))[1])
    
    def _hasIDInputFile(self, run_or_set_quality: BaseQuality) -> bool:
        """Confirms if a run or set_quality has ID type file in their inputFile

        For now, the ID types are recognised by ther filename extensions, including:
        '.mzid', '.pepxml', '.idxml', '.mztab'
        in various forms of spelling.

        Parameters
        ----------
        run_or_set_quality : BaseQuality
            the run or set quality collection to be confirmed

        Returns
        -------
        bool
            returns True if any of the notorious ID type files is present
        """
        idfext = ('.mzid', '.pepxml', '.idxml', '.mztab')  # NB case is all _lower_ and to be used after .lower() on target
        for input_file in run_or_set_quality.metadata.inputFiles:
            infilo = os.path.splitext(
                    os.path.basename(input_file.location))[0]
            infina = os.path.splitext(
                os.path.basename(input_file.name))[0]
            if infilo.lower().endswith(idfext) or \
                infina.lower().endswith(idfext):
                return True
        return False

    def _check_CVTerm_match(self, issue_type_category: str, cv_par: CvParameter, voc_par: Term, _document_collected_issues: bool = False):
        """Checks any cvParameter for correct definition and reference

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed 
        cv_par : CvParameter
            the parameter to be checked
        voc_par : Term
            the ontology term it is referencing
        _document_collected_issues : bool, optional
            for auto documentation this is set True, by default False

        """
        if _document_collected_issues:
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerm without definition", 4,
                                        f'Term instance used in file missing definition: '
                                        f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerms definition conflict", 5,
                                        f'Term instance used in file with definition different from ontology: '
                                        f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerms name conflict", 6,
                                        f'Term instance used in file with name different from ontology: '
                                        f'accession = {"auto_doc"}'))
            return
        
        cv_par.accession == voc_par.id
        cv_par.name == voc_par.name
        
        #warn if definition is empty or mismatch
        if not cv_par.description:
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerm without definition", 4,
                                        f'Term instance used in file missing definition: '
                                        f'accession = {cv_par.accession}'))
        elif cv_par.description != voc_par.definition:  # elif as the following error would be nonsensical for omitted definition
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerms definition conflict", 5,
                                        f'Term instance used in file with definition different from ontology: '
                                        f'accession = {cv_par.accession}'))
        if cv_par.name != voc_par.name:
            self.raising(issue_type_category, 
                         SemanticIssue("Used CVTerms name conflict", 6,
                                        f'Term instance used in file with name different from ontology: '
                                        f'accession = {cv_par.accession}'))
        return 
    
    def _check_CVTerm_use(self, issue_type_category: str, file_vocabularies: Dict[str,Ontology], _document_collected_issues: bool = False):
        """Checks any cvParameter for correct use according to definition and schema

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed 
        file_vocabularies : Dict[str,Ontology]
            the mzQC referenced vocabularies
        _document_collected_issues : bool, optional
            for auto documentation this is set True, by default False
        """
        if _document_collected_issues:
            self.raising(issue_type_category, 
                         SemanticIssue("Ambiguous CVTerms", 6,
                                        f'term found in multiple vocabularies = {"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Unknown CVTerm", 7,
                                        f'CV term used without matching ontology entry: '
                                        f'accession = {"auto_doc"}'))
            self._check_CVTerm_match(issue_type_category, None, None, _document_collected_issues)
            return
        
        # For all cv terms involved:
        for cv_parameter in self._get_cv_parameters(self.mzqc_obj):
            # Verify that the term exists in the CV.
            voc_par: List[SemanticIssue] = list(filter(None, [cvoc.get(cv_parameter.accession) for cvoc in file_vocabularies.values()]))
            if len(voc_par) > 1:
                # multiple choices for accession error
                occs = [str(o) for o in voc_par]
                self.raising(issue_type_category, 
                             SemanticIssue("Ambiguous CVTerms", 6,
                                        f'term found in multiple vocabularies = {",".join(occs)}'))
            elif len(voc_par) < 1:
                self.raising(issue_type_category, SemanticIssue("Unknown CVTerm", 7,
                                        f'CV term used without matching ontology entry: '
                                        f'accession = {cv_parameter.accession}'))
            else:
                self._check_CVTerm_match(issue_type_category, cv_parameter, voc_par[0], _document_collected_issues)
        return

    def _check_metric_use(self, issue_type_category: str, file_vocabularies: Dict[str,Ontology], _document_collected_issues: bool = False):
        """Checks any QC metric for correct use according to definition and schema

        Parameters
        ----------
        issue_type_category : str
            the issue type or category under which detected issues are filed 
        file_vocabularies : Dict[str,Ontology]
            the mzQC referenced vocabularies
        _document_collected_issues : bool, optional
            for auto documentation this is set True, by default False
        """
        if _document_collected_issues:
            self.raising(issue_type_category, 
                         SemanticIssue("ID based metric but no ID input file", 6,
                                        f'ID based metrics present but no ID input file could be found registered in the mzQC file: '
                                        f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, 
                         SemanticIssue("Metric uniqueness", 6, 
                                        f'Duplicate quality metric in a run/set: '
                                        f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric use", 5,
                                                f'Non-metric CV term used in metric context: '
                                                f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value non-table", 6,
                                                f'Table metric CV term used without being a table: '
                                                f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value non-column", 6,
                                                f'Table metric CV term used with non-column elements: '
                                                f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value disproportional table", 9,
                                                f'Table metric CV term used with differing column lengths: '
                                                f'accession = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value missing table column", 8,
                                                f'Table metric CV term used missing required column(s): '
                                                f'accession(s) = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value undefined table column", 5,
                                                f'Table metric CV term used with extra (undefined) columns: '
                                                f'accession(s) = {"auto_doc"}'))
            self.raising(issue_type_category, SemanticIssue("Metric value no-unit", 3,
                                                f'Metric CV term used without value unit specification. '
                                                f'accession(s) = {"auto_doc"}'))
            return
        
        metric_cvs = self._getVocabularyMetrics(file_vocabularies)
        table_cvs = self._getVocabularyTables(file_vocabularies)
        idmetric_cvs = self._getVocabularyIDMetrics(file_vocabularies)

        for run_or_set_quality in chain(self.mzqc_obj.runQualities,self.mzqc_obj.setQualities):
            # Check for ID metrics and if present if ID file is present in input
            if any([quality_metric.accession in idmetric_cvs for quality_metric in run_or_set_quality.qualityMetrics]):
                if not self._hasIDInputFile(run_or_set_quality):
                    self.raising(issue_type_category, SemanticIssue("ID based metric but no ID input file", 6,
                                                f'ID based metrics present but no ID input file could be found registered in the mzQC file: '
                                                f'run/set label = {run_or_set_quality.metadata.label}'))
            
            # Verify that quality metrics are unique within a run/setQuality.
            uniq_accessions: Set[str] = set()
            for quality_metric in run_or_set_quality.qualityMetrics:
                if quality_metric.accession in uniq_accessions:
                    self.raising(issue_type_category, SemanticIssue("Metric uniqueness", 6, 
                                                f'Duplicate quality metric in a run/set: '
                                                f'accession = {quality_metric.accession}'))
                else:
                    uniq_accessions.add(quality_metric.accession)
                # Verify that quality_metric actually is of metric type/relationship?
                if quality_metric.accession not in metric_cvs:
                    self.raising(issue_type_category, SemanticIssue("Metric use", 5,
                                                f'Non-metric CV term used in metric context: '
                                                f'accession = {quality_metric.accession}'))

                # check table's value types and column lengths
                if quality_metric.accession in table_cvs:
                    req_col_accs = {x.id for x in self._getRequiredCols(quality_metric.accession, file_vocabularies)[0]}
                    opt_col_accs = {x.id for x in self._getRequiredCols(quality_metric.accession, file_vocabularies)[1]}
                    
                    if not isinstance(quality_metric.value , dict):
                        self.raising(issue_type_category, SemanticIssue("Metric value non-table", 6,
                                                f'Table metric CV term used without being a table: '
                                                f'accession = {quality_metric.accession}'))
                    elif not all([isinstance(sv, list) for sv in quality_metric.value.values()]):
                        self.raising(issue_type_category, SemanticIssue("Metric value non-column", 6,
                                                f'Table metric CV term used with non-column elements: '
                                                f'accession = {quality_metric.accession}'))
                    elif len({len(sv) for sv in quality_metric.value.values()}) != 1:
                        self.raising(issue_type_category, SemanticIssue("Metric value disproportional table", 9,
                                                f'Table metric CV term used with differing column lengths: '
                                                f'accession = {quality_metric.accession}'))
                    elif not req_col_accs.issubset(set(quality_metric.value.keys())):
                        deviants = ','.join(req_col_accs.difference(set(quality_metric.value.keys())))
                        self.raising(issue_type_category, SemanticIssue("Metric value missing table column", 8,
                                                f'Table metric CV term used missing required column(s): '
                                                f'accession(s) = {deviants}'))
                    elif not set(quality_metric.value.keys()).issubset(req_col_accs.union(opt_col_accs)):
                        extras = ','.join(set(quality_metric.value.keys()).difference(req_col_accs.union(opt_col_accs)))
                        self.raising(issue_type_category, SemanticIssue("Metric value undefined table column", 5,
                                                f'Table metric CV term used with extra (undefined) columns: '
                                                f'accession(s) = {extras}'))
                else:
                    if quality_metric.unit is None or quality_metric.unit == "":
                        self.raising(issue_type_category, SemanticIssue("Metric value no-unit", 3,
                                                f'Metric CV term used without value unit specification. '
                                                f'accession(s) = {quality_metric.accession}'))
        return

    def string_export(self) -> Dict[str,List[str]]:
        """Helper function to properly export the validation results

        For easy compatibility with the validation apps from the repositories accessories.

        Returns
        -------
        Dict[str,List[str]]
            dict of list of issues formatted as str
        """
        if self._invalid_mzqc_obj:
            return {"general": "incompatible object given to validation"}
        else:
            return {k: [i._to_string() for i in v] for k,v in self.items()}

    def _document_collected_issues(self):
        """Collects all issues theoretically generated by a validate call

        The issues are collected as usual, but are artificially generated. See the 
        validate function documentation for more details and check its use in the 
        SemanticCheck tests.
        """
        return self.validate(max_errors=0, load_local=True, keep_issues=False, _document_collected_issues=True)

    def validate(self, max_errors: int = 0, load_local: bool = False, keep_issues: bool = False, _document_collected_issues: bool = False):
        """Validates the object given during class initialisation, considers a number of parameters

        Note before adding new checks: create functions to check specific types of issues, 
        name the group or select an existing group and add new SemanticIssues to self under 
        that group's name as key with the `raising` function. Also add a method for synthetic
        generation of these new issues given the  _document_collected_issues flag. Like that,
        the name, severity level, and error message gets automatically documented, also in the
        validator apps of the accessories to the pymzqc repository. Should a new group name be 
        introduced, it is also necessary to add this name to the `issue_types_genreated` to 
        ensure proper auto_doc functionality.

        The validation result is kept in the object itself, accessible through the UserDict 
        and additional member attributes (see class doc). A convenience function to 
        export the list of stringified dict of SemanticIssue lists, e.g. with the apps 
        from the pymzqc's repository accessories, is provided with `string_export`.

        Parameters
        ----------
        max_errors : int, optional
            the maximum number of SemanticIssues detected before the validation will raise a ValidationIssue, by default 0 for no limit
        load_local : bool, optional
            flag to indicate if referenced local files should be attempted to load, by default False does not make sense for online validation
        keep_issues : bool, optional
            flag to indicate if any SemanticIssues from previous should _NOT_ be cleared, by default False
        _document_collected_issues : bool, optional
            flag to indicate that every possible SemanticIssue is to be auto_doc generated, by default False
        """
        # needs to be kept up-to-date to document the implemented issue type or categories
        issue_types_genreated = ['input files', 'metric use', 'ontology load errors',
                                 'ontology term errors', 'label uniqueness']
        
        if not keep_issues:
            self.clear()
            for i in issue_types_genreated:
                self[i] = list()
        else:
           for i in set(issue_types_genreated) - set(self.keys()):
               self[i] = list()

        self._max_errors = max_errors
        self._load_local = load_local
        self._keep_issues = keep_issues
        self._invalid_mzqc_obj = False
        self._exceeded_errors = False

        # Stop early if we can't recognise the data object and return a simplified validation_errs dict
        if type(self.mzqc_obj) != MzQcFile:
            self._invalid_mzqc_obj = True
            return
        
        # Check that label (metadata) must be unique in the file
        # at some point with max_error > 0 this will raise an ValidationError for max_error exceeded
        # so either try_catch or more fancy with contextmanger to manage max_error execution
        self._check_label_uniqueness('label uniqueness', _document_collected_issues)

        # Check that all cvs referenced are linked to valid ontology
        file_vocabularies = self._load_and_check_Vocabularies('ontology load errors',
                                                             load_local,
                                                             _document_collected_issues)

        # Check that terms used are defined and used in the right place
        self._check_CVTerm_use('ontology term errors', file_vocabularies, _document_collected_issues)

        # Check that qualityParameters are used as defined and unique within a run/setQuality
        self._check_metric_use('metric use', file_vocabularies, _document_collected_issues)

        # Regarding metadata, verify that input files are consistent and unique.
        self._check_InputFile_consistency('input files', _document_collected_issues)
        
        return 
