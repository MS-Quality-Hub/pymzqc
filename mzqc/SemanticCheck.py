__author__ = 'bittremieux, walzer'
import json
import mzqc
import os
import urllib.request
from typing import Dict, List, Set, Union, Tuple, Any
from mzqc.MZQCFile import MzQcFile, BaseQuality, RunQuality, SetQuality, QualityMetric, MetaDataParameters, CvParameter
from itertools import chain
from dataclasses import dataclass, field

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

# TODO The whole SemanticIssue class probably needs a proper validation object (with place_s_ for 
# error/warning/other) to collect all the information accumulating while going through the validation
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
        return self.name + " of severity "+ str(self.severity) + "and message:" + self.message

class SemanticCheck(object):
    def __init__(self, version: str=""):
        self.version = version
        self.issues = dict()

    def _get_cv_parameters(self, val: object):
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

    def _getVocabularies(self, mzqc_obj: MzQcFile, load_local=False) -> Tuple[Dict[str,Ontology], List[SemanticIssue]]:
        #vocs = {cve.name: Ontology(cve.uri) for cve in mzqc_obj.controlledVocabularies}
        vocs = dict()
        errs = list()
        for cve in mzqc_obj.controlledVocabularies:
            try:
                # check if local CV was used
                if load_local:
                    loc = cve.uri
                    if loc.startswith('file://'):
                        loc = loc[len('file://'):]
                        errs.append(SemanticIssue("Loading Vocabulary", 5, 
                                                  f'Loading the following local ontology referenced in mzQC file: {loc}'))
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(loc, import_depth=0)
                else:
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(cve.uri, import_depth=0)
            except Exception as e:
                errs.append(SemanticIssue("Loading Vocabulary", 5, 
                                          f'Error loading the following online ontology referenced in mzQC file: {e}'))
        return vocs, errs

    def _inputFileConsistency(self, mzqc_obj: MzQcFile) -> List[SemanticIssue]:
        input_file_errors = list()
        input_file_sets = list()
        for quality in chain(mzqc_obj.runQualities,mzqc_obj.setQualities):
            one_input_file_set = set()
            for input_file in quality.metadata.inputFiles:
                # filename and location
                infilo = os.path.splitext(
                    os.path.basename(input_file.location))[0]
                if input_file.name != infilo:
                    input_file_errors.append(SemanticIssue("Input Files", 4,
                        f'Inconsistent file name and location: {input_file.name}/{infilo}'))
                one_input_file_set.add(input_file.location)

            # if more than 2 inputs but just one location
            if len(quality.metadata.inputFiles) != one_input_file_set:
                input_file_errors.append(SemanticIssue("Input Files", 6,
                                                       f'Duplicate inputFile locations within a metadata object: '
                                                       f'accession = {one_input_file_set}'))

            # check duplicates 
            if one_input_file_set in input_file_sets:
                    input_file_errors.append(SemanticIssue("Input Files", 7,
                                                f'Duplicate input files in a run/set: '
                                                f'accession = {one_input_file_set}'))
            else:
                input_file_sets.append(one_input_file_set)
        return input_file_errors

    def _getVocabularyMetrics(self, filevocabularies: Dict[str,Ontology]) -> Set[str]:
        metricsubclass_sets_list = list()
        for k,v in filevocabularies.items():
            try:
                metricsubclass_sets_list.append({x.id for x in v['MS:4000002'].subclasses().to_set()})
            except KeyError:
                pass
        return set().union(chain.from_iterable(metricsubclass_sets_list))

    def _getVocabularyIDMetrics(self, filevocabularies: Dict[str,Ontology]) -> Set[str]:
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
        tablesubclass_sets_list = list()
        for k,v in filevocabularies.items():
            try:
                tablesubclass_sets_list.append({x.id for x in v['MS:4000005'].subclasses().to_set()})
            except KeyError:
                pass
        return set().union(chain.from_iterable(tablesubclass_sets_list))

    def _getRequiredCols(self, accession: str, filevocabularies: Dict[str,Ontology]) -> Tuple[Set[Term],Set[Term]]:
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
    
    def _hasIDInputFile(self, run_or_set_quality) -> bool:
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

    def _cvmatch(self, cv_par: CvParameter, voc_par: Term) -> List[SemanticIssue]:
        cv_par.accession == voc_par.id
        cv_par.name == voc_par.name
        
        term_errs: List[SemanticIssue] = list()
        #warn if definition is empty or mismatch
        if not cv_par.description:
            term_errs.append(SemanticIssue("Used CVTerms", 4,
                                            f'CV term used without accompanying term definition: '
                                            f'accession = {cv_par.accession}'))
        elif cv_par.description != voc_par.definition:  # elif as the following error would be nonsensical for omitted definition
            term_errs.append(SemanticIssue("Used CVTerms", 5,
                                            f'CV term used with definition different from ontology: '
                                            f'accession = {cv_par.accession}'))
        if cv_par.name != voc_par.name:
            term_errs.append(SemanticIssue("Used CVTerms", 6,
                                            f'CV term used with differing name from ontology: '
                                            f'accession = {cv_par.accession}'))
        return term_errs
    
    def _transform_for_return(self):
        return {k: [i._to_string() for i in v] for k,v in self.issues.items()}

    def validate(self, mzqc_obj: MzQcFile, max_errors:int=0, load_local:bool=False, keep_issues=False):
        if keep_issues:
            self.issues = dict()

        # Stop early if we can't recognise the data object and return a simplified validation_errs dict
        if type(mzqc_obj) != MzQcFile:
            return {"semantic validation": {"general": "incompatible object given to validation"} }

        # Check that label (metadata) must be unique in the file
        uniq_labels = set()
        label_errs = list()
        for qle in chain(mzqc_obj.runQualities,mzqc_obj.setQualities):
            if qle.metadata.label in uniq_labels:
                label_errs.append(SemanticIssue("Metadata labels", 6,
                    "Run/SetQuality label {} is not unique in file!".format(qle.metadata.label)))
            else: 
                uniq_labels.add(qle.metadata.label)
        self.issues['label uniqueness'] = label_errs

        # Check that all cvs referenced are linked to valid ontology
        file_vocabularies, voc_errs = self._getVocabularies(mzqc_obj, load_local=load_local)
        # check if ontologies are listed multiple times (different versions etc)
        self.issues['ontology load errors'] = voc_errs

        # - check max_error
        if max_errors > 0:
            if sum([len(x) for x in self.issues.values()]) > max_errors:
                self.issues['general'] = self.issues.get('general', list())
                self.issues['general'].append(
                    ValidationError("Maximum number of errors incurred ({me} < {ie}), aborting!".format(
                    ie=sum([len(x) for x in self.issues.values()]), me = max_errors))
                )
                self.errors = self.issues
                return {k: [i._to_string() for i in v] for k,v in self.issues.items()}

        # For all cv terms involved:
        term_errs = list()
        for cv_parameter in self._get_cv_parameters(mzqc_obj):
            # Verify that the term exists in the CV.
            if not any(cv_parameter.accession in cvoc for cvoc in file_vocabularies.values()):
                # cv not found error
                term_errs.append(SemanticIssue("Used CVTerms", 7,
                                            f'CV term used not found error: '
                                            f'accession = {cv_parameter.accession} ; '
                                            f'name = {cv_parameter.name} '))
            # Check that cv in file and obo must match in id,name,type
            else:
                voc_par: List[SemanticIssue] = list(filter(None, [cvoc.get(cv_parameter.accession) for cvoc in file_vocabularies.values()]))
                if len(voc_par) > 1:
                    # multiple choices for accession error
                    occs = [str(o) for o in voc_par]
                    term_errs.append(SemanticIssue("Used CVTerms", 5,
                                            f'Ambiguous term error: '
                                            f'occurrences = {",".join(occs)}'))
                elif len(voc_par) < 1:
                    term_errs.append(SemanticIssue("Used CVTerms", 7,
                                            f'CV term used without matching ontology entry: '
                                            f'accession = {cv_parameter.accession}'))
                else:
                    cv_err = self._cvmatch(cv_parameter, voc_par[0])
                    if cv_err:
                        term_errs.extend(cv_err)
        self.issues['ontology term errors'] = term_errs

        # check max_error
        if max_errors > 0:
            if sum([len(x) for x in self.issues.values()]) > max_errors:
                self.issues['general'] = self.issues.get('general', list())
                self.issues['general'].append(
                    ValidationError("Maximum number of errors incurred ({me} < {ie}), aborting!".format(
                    ie=sum([len(x) for x in self.issues.values()]), me = max_errors))
                )
                self.errors = self.issues
                return {k: [i._to_string() for i in v] for k,v in self.issues.items()}

        # TODO #
        # Check that qualityParameters are unique within a run/setQuality.
        metrics_uniq_warns = list()
        actual_metric_warns = list()
        metric_type_errs = list()
        metric_cvs = self._getVocabularyMetrics(file_vocabularies)
        table_cvs = self._getVocabularyTables(file_vocabularies)
        idmetric_cvs = self._getVocabularyIDMetrics(file_vocabularies)
        print(idmetric_cvs)
        for run_or_set_quality in chain(mzqc_obj.runQualities,mzqc_obj.setQualities):
            # Check for ID metrics and if present if ID file is present in input
            if any([quality_metric.accession in idmetric_cvs for quality_metric in run_or_set_quality.qualityMetrics]):
                if not self._hasIDInputFile(run_or_set_quality):
                    metrics_uniq_warns.append(SemanticIssue("Metric Usage", 6,
                                                f'ID based metrics present but no ID input file could be found registered in the mzQC file: '
                                                f'accession = {run_or_set_quality.metadata.label}'))
            
            # Verify that quality metrics are unique within a run/setQuality.
            uniq_accessions: Set[str] = set()
            for quality_metric in run_or_set_quality.qualityMetrics:
                if quality_metric.accession in uniq_accessions:
                    metrics_uniq_warns.append(SemanticIssue("Metric Usage", 6, 
                                                f'Duplicate quality metric in a run/set: '
                                                f'accession = {quality_metric.accession}'))
                else:
                    uniq_accessions.add(quality_metric.accession)
                # Verify that quality_metric actually is of metric type/relationship?
                if quality_metric.accession not in metric_cvs:
                    actual_metric_warns.append(SemanticIssue("Metric Use", 5,
                                                f'Non-metric CV term used in metric context: '
                                                f'accession = {quality_metric.accession}'))

                # TODO check metric term units

                # check table's value types and column lengths
                if quality_metric.accession in table_cvs:
                    req_col_accs = {x.id for x in self._getRequiredCols(quality_metric.accession, file_vocabularies)[0]}
                    opt_col_accs = {x.id for x in self._getRequiredCols(quality_metric.accession, file_vocabularies)[1]}
                    print(quality_metric.name)
                    print("req!",req_col_accs)
                    print("opt!",opt_col_accs)
                    
                    if not isinstance(quality_metric.value , dict):
                        metric_type_errs.append(SemanticIssue("Metric Use", 6,
                                                f'Table metric CV term used without being a table: '
                                                f'accession = {quality_metric.accession}'))
                    elif not all([isinstance(sv, list) for sv in quality_metric.value.values()]):
                        metric_type_errs.append(SemanticIssue("Metric Use", 6,
                                                f'Table metric CV term used with non-column elements: '
                                                f'accession = {quality_metric.accession}'))
                    elif len({len(sv) for sv in quality_metric.value.values()}) != 1:
                        metric_type_errs.append(SemanticIssue("Metric Use", 9,
                                                f'Table metric CV term used with differing column lengths: '
                                                f'accession = {quality_metric.accession}'))
                    elif not req_col_accs.issubset(set(quality_metric.value.keys())):
                        deviants = ','.join(req_col_accs.difference(set(quality_metric.value.keys())))
                        metric_type_errs.append(SemanticIssue("Metric Use", 8,
                                                f'Table metric CV term used missing required column(s): '
                                                f'accession(s) = {deviants}'))
                    elif not set(quality_metric.value.keys()).issubset(req_col_accs.union(opt_col_accs)):
                        extras = ','.join(set(quality_metric.value.keys()).difference(req_col_accs.union(opt_col_accs)))
                        print("extras?",extras)
                        metric_type_errs.append(SemanticIssue("Metric Use", 5,
                                                f'Table metric CV term used with extra (undefined) columns: '
                                                f'accession(s) = {extras}'))
                    try:
                        print("cols~",set(quality_metric.value.keys()))
                    except:
                        pass

        self.issues['metric uniqueness'] = metrics_uniq_warns
        if len(metric_cvs) < 1:
            actual_metric_warns.append(SemanticIssue("Metric Use", 6,
                                                f'No metric CV terms found in the given files ontologies!'))
        self.issues['metric usage errors'] = actual_metric_warns
        self.issues['value type errors'] = metric_type_errs

        #check max_error
        if max_errors > 0:
            if sum([len(x) for x in self.issues.values()]) > max_errors:
                self.issues['general'] = self.issues.get('general', list())
                self.issues['general'].append(
                    ValidationError("Maximum number of errors incurred ({me} < {ie}), aborting!".format(
                    ie=sum([len(x) for x in self.issues.values()]), me = max_errors))
                )
                self.errors = self.issues
                return {k: [i._to_string() for i in v] for k,v in self.issues.items()}

        # Regarding metadata, verify that input files are consistent and unique.
        self.issues['input files'] = self._inputFileConsistency(mzqc_obj)
        
        # keep last check and return
        self.errors = self.issues

        # return dict of list of stringyfied errors
        return self._transform_for_return()
