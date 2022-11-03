__author__ = 'walzer'
# Everything needs to be prefixed with test in order to be picked up by pytest,
# i.e. TestClass() and test_function()
import pytest
from mzqc.SemanticCheck import SemanticCheck
from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
import warnings


"""
    Semantic tests with pymzqc
     
    NOTE: warnings from the semantic test class (esp. those from fastobo or 
        pronto) are ignored!
"""


def test_SemanticCheck_nonMetricTerm():
    infi = "tests/examples/individual-runs_nonMetricTerm.mzQC"  # test good detection
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    # assert "metric usage errors" in sem_val.keys()
    print(sem_val.keys())
    assert (
        "Non-metric CV term used in metric context: accession = MS:1002040"
        in sem_val.get("metric usage errors", list())
    )


def test_SemanticCheck_tableExtraColumn():
    infi = "tests/examples/individual-runs_tableExtraColumn.mzQC"  # test good detectin
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert "value type errors" in sem_val.keys()
    assert (
        "WARNING: Table metric CV term used with extra (undefined) columns: accession(s) = wron col"
        in sem_val.get("value type errors", list())
    )


def test_SemanticCheck_wrongTermName():
    infi = "tests/examples/individual-runs_wrongTermName.mzQC"  # test good detectin
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert "value type errors" in sem_val.keys()
    assert (
        "Table metric CV term used without being a table: accession = MS:4000063"
        in sem_val.get("value type errors", list())
    )


def test_SemanticCheck_tableIncomplete():
    infi = "tests/examples/individual-runs_tableIncomplete.mzQC"  # test good detectin
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert "value type errors" in sem_val.keys()
    assert (
        "Table metric CV term used missing required column(s): accession(s) = UO:0000191"
        in sem_val.get("value type errors", list())
    )


def test_SemanticCheck_unequalTableCols():
    infi = "tests/examples/individual-runs_unequalTableCols.mzQC"  # test good detection
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert "value type errors" in sem_val.keys()
    assert (
        "Table metric CV term used with differing column lengths: accession = MS:4000063"
        in sem_val.get("value type errors", list())
    )


def test_SemanticCheck_duplicateMetric():
    infi = "tests/examples/individual-runs_duplicateMetric.mzQC"  # test good detection
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert "metric uniqueness" in sem_val.keys()
    assert "Duplicate quality metric in a run/set: accession = MS:4000059" in sem_val.get(
        "metric uniqueness", list()
    )


def test_SemanticCheck_success():
    infi = "tests/examples/individual-runs.mzQC"  # success test
    with open(infi, "r") as f:
        mzqcobject = mzqc_io.from_json(f)

    assert type(mzqcobject) == mzqc_file
    removed_items = list(
        filter(
            lambda x: not (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )
    mzqcobject.controlledVocabularies = list(
        filter(
            lambda x: (x.uri.startswith("http") or x.uri.startswith("file://")),
            mzqcobject.controlledVocabularies,
        )
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqcobject, load_local=True).validate()

    assert len(sem_val.get("label uniqueness", list())) == 0
    assert len(sem_val.get("metric uniqueness", list())) == 0
    assert len(sem_val.get("metric usage errors", list())) == 0
    assert len(sem_val.get("ontology load errors", list())) == 0
    assert len(sem_val.get("value type errors", list())) == 0
    assert all(
        [x.startswith("WARNING") for x in sem_val.get("ontology term errors", list())]
    )
