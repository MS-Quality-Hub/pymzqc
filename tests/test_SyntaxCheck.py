__author__ = "walzer"

# Everything needs to be prefixed with test in order to be picked up by pytest,
# i.e. TestClass() and test_function()
import pytest
import mzqc.MZQCFile as mzqc_lib
from mzqc.SyntaxCheck import SyntaxCheck


def test_SyntaxCheck_synth():
    cvt = mzqc_lib.CvParameter(accession="TEST:123", name="testname", value=99)
    infi = mzqc_lib.InputFile(
        name="file.raw",
        location="file:///dev/null",
        file_format=mzqc_lib.CvParameter("MS:1000584", "mzML format"),
        file_properties=[
            mzqc_lib.CvParameter(
                accession="MS:1000747",
                name="completion time",
                value="2017-12-08-T15:38:57Z",
            )
        ],
    )
    anso = mzqc_lib.AnalysisSoftware(
        accession="QC:9999999", name="bigwhopqc", version="1.2.3", uri="file:///dev/null"
    )  # isn't requiring a uri a bit too much?
    meta = mzqc_lib.MetaDataParameters(
        input_files=[infi], analysis_software=[anso], label="test_label"
    )
    qm = mzqc_lib.QualityMetric(accession="QC:4000053", name="RT duration", value=99)
    qm2 = mzqc_lib.QualityMetric(
        accession="QC:4000061", name="Maximal MS2 frequency", value=999
    )
    qm3 = mzqc_lib.QualityMetric(
        accession="QC:4000055", name="MS1 quantiles RT fraction", value=9
    )
    rq = mzqc_lib.RunQuality(metadata=meta, quality_metrics=[qm, qm2])
    sq = mzqc_lib.SetQuality(metadata=meta, quality_metrics=[qm3])
    cv = mzqc_lib.ControlledVocabulary(name="QCvocab", uri="www.qc.ml")
    cv2 = mzqc_lib.ControlledVocabulary(name="TEST", uri="www.eff.off")
    mzqc = mzqc_lib.MzQcFile(
        version="1.0.0",
        run_qualities=[rq],
        set_qualities=[sq],
        controlled_vocabularies=[cv, cv2],
    )
    # with open('tests/mzqc_lib_out.mzqc', 'w') as f:
    #     f.write("{ \"mzQC\": " + mzqc_lib.JsonSerialisable.ToJson(mzqc) + " }")

    syn_check = SyntaxCheck()
    syn_check.validate('{ "mzQC": ' + mzqc_lib.JsonSerialisable.to_json(mzqc) + " }")


def test_SyntaxCheck_brokenAnalysisSoftware():
    """
    # test good detectin schema invalid
    """
    infi = "tests/examples/individual-runs_brokenAnalysisSoftware.mzQC"
    with open(infi, "r") as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    assert (
        syn_val.get("schema validation", "")
        == "'version' is a required property @ [mzQC][runQualities][0][metadata][analysisSoftware][1]"
    )


def test_SyntaxCheck_extraContent():
    """
    test good detectin schema invalid, also QC:000 terms unknown

    """
    infi = "tests/examples/individual-runs_extraJSONcontent.mzQC"
    with open(infi, "r") as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    assert (
        syn_val.get("schema validation", "")
        == "Additional properties are not allowed ('test' was unexpected) @ "
    )


def test_SyntaxCheck_noOuter():
    """
    # No mzQC content found! no mzQC object no detectin
    """
    infi = "tests/examples/individual-runs-noOuter.json"
    with open(infi, "r") as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    offenders = [
        "Additional properties are not allowed (",
        "controlledVocabularies",
        "creationDate",
        "version",
        "description",
        "contactAddress",
        "contactName",
        "runQualities",
        "were unexpected) @",
    ]
    assert all([x in syn_val.get("schema validation", "") for x in offenders])
