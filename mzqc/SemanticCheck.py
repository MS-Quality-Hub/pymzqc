__author__ = "bittremieux, walzer"

import os
import sys
from contextlib import contextmanager
from itertools import chain
from typing import Dict, List, Set, Tuple

from jsonschema.exceptions import ValidationError
from pronto import Ontology, Term

from mzqc.MZQCFile import (
    CvParameter,
    MetaDataParameters,
    MzQcFile,
    RunQuality,
    SetQuality,
)


@contextmanager
def suppress_verbose_modules():
    with open(os.devnull, "w") as devnull:
        sys_stderr_bak = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = sys_stderr_bak


class SemanticError(ValidationError):
    """Base class for exceptions in this module."""

    pass


class SemanticCheck(object):
    def __init__(self, mzqc_obj: MzQcFile, load_local=False, version: str = ""):
        self.errors = {}
        self.version = version

        if type(mzqc_obj) != MzQcFile:
            raise ValidationError(
                {
                    "semantic validation": {
                        "general": "incompatible object given to validation"
                    }
                }
            )
        self.mzqc_obj = mzqc_obj
        self.file_vocabularies = self._get_vocabularies(mzqc_obj, load_local=load_local)

    def _get_cv_parameters(self, val: object):
        if hasattr(val, "accession"):
            yield val
        elif isinstance(val, List):
            for v in val:
                yield from self._get_cv_parameters(v)
        elif isinstance(val, (MzQcFile, SetQuality, RunQuality, MetaDataParameters)):
            for attr, value in vars(val).items():
                yield from self._get_cv_parameters(value)
        else:
            # recursion dead-end
            pass

    def _get_vocabularies(
        self, mzqc_obj: MzQcFile, load_local=False
    ) -> Dict[str, Ontology]:
        # vocs = {cve.name: Ontology(cve.uri) for cve in mzqc_obj.controlledVocabularies}
        vocs = dict()
        errs = list()
        for cve in mzqc_obj.controlledVocabularies:
            try:
                if load_local:
                    loc = cve.uri
                    if loc.startswith("file://"):
                        loc = loc[len("file://") :]
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(loc)
                else:
                    with suppress_verbose_modules():
                        vocs[cve.name] = Ontology(cve.uri)
            except Exception as e:
                errs.append(
                    SemanticError(
                        f"Error loading the following ontology referenced in file: {e}"
                    )
                )

        self.errors["ontology_load_errors"] = errs
        return vocs

    def _input_file_consistency(self) -> List[SemanticError]:
        input_file_errors = list()
        input_file_sets = list()
        for quality in chain(self.mzqc_obj.runQualities, self.mzqc_obj.setQualities):
            one_input_file_set = set()
            for input_file in quality.metadata.inputFiles:
                # filename and location
                infilo = os.path.splitext(os.path.basename(input_file.location))[0]
                if input_file.name != infilo:
                    input_file_errors.append(
                        SemanticError(
                            f"Inconsistent file name and location: {input_file.name}/{infilo}"
                        )
                    )
                one_input_file_set.add(input_file.location)

            # if more than 2 inputs but just one location
            if len(quality.metadata.inputFiles) != one_input_file_set:
                input_file_errors.append(
                    SemanticError(
                        f"Duplicate inputFile locations within a metadata object: "
                        f"accession = {one_input_file_set}"
                    )
                )

            # check duplicates
            if one_input_file_set in input_file_sets:
                input_file_errors.append(
                    SemanticError(
                        f"Duplicate quality metric in a run/set: "
                        f"accession = {one_input_file_set}"
                    )
                )
            else:
                input_file_sets.append(one_input_file_set)
        return input_file_errors

    def _get_vocabulary_metrics(self) -> Set[str]:
        metric_subclass_sets_list = list()
        for k, v in self.file_vocabularies.items():
            try:
                metric_subclass_sets_list.append(
                    {x.id for x in v["MS:4000002"].subclasses().to_set()}
                )
            except KeyError:
                pass
        return set().union(chain.from_iterable(metric_subclass_sets_list))

    def _get_vocabulary_tables(self) -> Set[str]:
        table_subclass_sets_list = list()
        for k, v in self.file_vocabularies.items():
            try:
                table_subclass_sets_list.append(
                    {x.id for x in v["MS:4000005"].subclasses().to_set()}
                )
            except KeyError:
                pass
        return set().union(chain.from_iterable(table_subclass_sets_list))

    def _get_required_cols(self, accession: str) -> Tuple[Set[Term], Set[Term]]:
        tab_def = None
        for k, v in self.file_vocabularies.items():
            try:
                tab_def = v[accession]
                break
            except KeyError:
                pass
        if not tab_def:
            return set(), set()
        else:
            return set(
                next(
                    filter(
                        lambda x: x[0].name == "has_column", tab_def.relationships.items()
                    ),
                    (None, frozenset()),
                )[1]
            ), set(
                next(
                    filter(
                        lambda x: x[0].name == "has_optional_column",
                        tab_def.relationships.items(),
                    ),
                    (None, frozenset()),
                )[1]
            )

    def _cv_match(self, cv_par: CvParameter, voc_par: Term) -> List[SemanticError]:
        assert cv_par.accession == voc_par.id
        assert cv_par.name == voc_par.name

        term_errs: List[SemanticError] = list()
        # warn if definition is empty or mismatch
        if not cv_par.description:
            term_errs.append(
                SemanticError(
                    f"WARNING: CV term used without accompanying term definition: "
                    f"accession = {cv_par.accession}"
                )
            )
        elif (
            cv_par.description != voc_par.definition
        ):  # elif as the following error would be nonsensical for omitted definition
            term_errs.append(
                SemanticError(
                    f"CV term used with definition different from ontology: "
                    f"accession = {cv_par.accession}"
                )
            )

        if cv_par.name != voc_par.name:
            term_errs.append(
                SemanticError(
                    f"CV term used with differing name from ontology: "
                    f"accession = {cv_par.accession}"
                )
            )

        # TODO this (& the whole SemanticError class) probably needs a proper validation object (with place_s_ for
        # error/warning/other messages) to collect all the stuff while going through the validation
        return term_errs

    def validate(self):
        # TODO incorporate version when SemanticValidation may differ between versions
        # ! Semantic validation of the JSON file.
        # ? Check that label (metadata) must be unique in the file
        # ? Verify that the term exists in the CV.
        # ? Check that qualityParameters are unique within a run/setQuality.
        # ? Check that all cvs referenced are linked to valid ontology
        # ? Check that all columns in tables have same length
        # ? Check that cv value has all attributes referred in cv
        # ?? Check that multi-file metrics refer to existing filenames.
        # ?? Check that filenames are unique within a run/setQuality. #50

        # create validation error list object
        validation_errs = dict()  # need to keep it flexible

        # ? Check that label (metadata) must be unique in the file
        uniq_labels = set()
        label_errs = list()
        for qle in chain(self.mzqc_obj.runQualities, self.mzqc_obj.setQualities):
            if qle.metadata.label in uniq_labels:
                label_errs.append(
                    ValidationError(
                        "Run/SetQuality label {} is not unique in file!".format(
                            qle.metadata.label
                        )
                    )
                )
            else:
                uniq_labels.add(qle.metadata.label)
        validation_errs["label uniqueness"] = label_errs

        # For all cv terms involved:
        term_errs = list()
        for cv_parameter in self._get_cv_parameters(self.mzqc_obj):

            # ? Verify that the term exists in the CV.
            if not any(
                cv_parameter.accession in cvoc for cvoc in self.file_vocabularies.values()
            ):
                # cv not found error
                term_errs.append(
                    SemanticError(
                        f"term used not found error: "
                        f"accession = {cv_parameter.accession} ; "
                        f"name = {cv_parameter.name} "
                    )
                )
            # ? Check that cv in file and obo must match in id,name,type
            else:
                voc_par: List[SemanticError] = list(
                    filter(
                        None,
                        [
                            cvoc.get(cv_parameter.accession)
                            for cvoc in self.file_vocabularies.values()
                        ],
                    )
                )
                if len(voc_par) > 1:
                    # multiple choices for accession error
                    occs = [str(o) for o in voc_par]
                    term_errs.append(
                        SemanticError(
                            f"Ambiguous term error: " f'occurrences = {",".join(occs)}'
                        )
                    )
                elif len(voc_par) < 1:
                    term_errs.append(
                        SemanticError(
                            f"term used without matching ontology entry: "
                            f"accession = {cv_parameter.accession}"
                        )
                    )
                else:
                    cv_err = self._cv_match(cv_parameter, voc_par[0])
                    if cv_err:
                        term_errs.extend(cv_err)
        self.errors["ontology term errors"] = term_errs

        # ? Check that qualityParameters are unique within a run/setQuality.
        metrics_uniq_warns = list()
        actual_metric_warns = list()
        metric_type_errs = list()
        metric_cvs = self._get_vocabulary_metrics()
        table_cvs = self._get_vocabulary_tables()
        for run_or_set_quality in chain(
            self.mzqc_obj.runQualities, self.mzqc_obj.setQualities
        ):
            # Verify that quality metrics are unique within a run/setQuality.
            uniq_accessions: Set[str] = set()
            for quality_metric in run_or_set_quality.qualityMetrics:
                if quality_metric.accession in uniq_accessions:
                    metrics_uniq_warns.append(
                        SemanticError(
                            f"Duplicate quality metric in a run/set: "
                            f"accession = {quality_metric.accession}"
                        )
                    )
                else:
                    uniq_accessions.add(quality_metric.accession)
                # Verify that quality_metric actually is of metric type/relationship?
                if quality_metric.accession not in metric_cvs:
                    actual_metric_warns.append(
                        SemanticError(
                            f"Non-metric CV term used in metric context: "
                            f"accession = {quality_metric.accession}"
                        )
                    )

                # check value types and column lengths
                if quality_metric.accession in table_cvs:
                    req_col_accs = {
                        x.id for x in self._get_required_cols(quality_metric.accession)[0]
                    }
                    opt_col_accs = {
                        x.id for x in self._get_required_cols(quality_metric.accession)[1]
                    }

                    if not isinstance(quality_metric.value, dict):
                        metric_type_errs.append(
                            SemanticError(
                                f"Table metric CV term used without being a table: "
                                f"accession = {quality_metric.accession}"
                            )
                        )
                    elif not all(
                        [isinstance(sv, list) for sv in quality_metric.value.values()]
                    ):
                        metric_type_errs.append(
                            SemanticError(
                                f"Table metric CV term used with non-column elements: "
                                f"accession = {quality_metric.accession}"
                            )
                        )
                    elif len({len(sv) for sv in quality_metric.value.values()}) != 1:
                        metric_type_errs.append(
                            SemanticError(
                                f"Table metric CV term used with differing column lengths: "
                                f"accession = {quality_metric.accession}"
                            )
                        )
                    elif not req_col_accs.issubset(set(quality_metric.value.keys())):
                        deviants = ",".join(
                            req_col_accs.difference(set(quality_metric.value.keys()))
                        )
                        metric_type_errs.append(
                            SemanticError(
                                f"Table metric CV term used missing required column(s): "
                                f"accession(s) = {deviants}"
                            )
                        )
                    elif not set(quality_metric.value.keys()).issubset(
                        req_col_accs.union(opt_col_accs)
                    ):
                        extras = ",".join(
                            set(quality_metric.value.keys()).difference(
                                req_col_accs.union(opt_col_accs)
                            )
                        )
                        metric_type_errs.append(
                            SemanticError(
                                f"WARNING: Table metric CV term used with extra "
                                f"(undefined) columns: accession(s) = {extras}"
                            )
                        )

        self.errors["metric uniqueness"] = metrics_uniq_warns
        if len(metric_cvs) < 1:
            actual_metric_warns.append(
                SemanticError(f"No dedicated metric CV terms found in file ontologies!")
            )
        self.errors["metric usage errors"] = actual_metric_warns
        self.errors["value type errors"] = metric_type_errs

        # Regarding metadata, verify that input files are consistent and unique.
        self.errors["input files"] = self._input_file_consistency()

        # return dict of list of stringyfied errors
        return {k: [str(i) for i in v] for k, v in validation_errs.items()}
