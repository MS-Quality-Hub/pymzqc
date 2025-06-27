__author__ = 'walzer'
import pytest  # Eeeeeeverything needs to be prefixed with test in order to be picked up by pytest, i.e. TestClass() and test_function()
import json
from mzqc.MZQCFile import MzQcFile as mzqc_file
import mzqc.MZQCFile as mzqc_lib
from mzqc.SyntaxCheck import SyntaxCheck

# The validation error will include this disclaimer before the first error message:
SCHEMA_VERSION_DISCLAIMER = "INFO - using schema: https://raw.githubusercontent.com/HUPO-PSI/mzQC/main/schema/mzqc_schema.json"

def test_SyntaxCheck_synth():
    cvt = mzqc_lib.CvParameter(accession="TEST:123", name="testname", value=99)
    infi = mzqc_lib.InputFile(name="file.raw",location="file:///dev/null",
                        fileFormat=mzqc_lib.CvParameter("MS:1000584", "mzML format"),
                        fileProperties=[mzqc_lib.CvParameter(accession="MS:1000747",
                                                        name="completion time",
                                                        value="2017-12-08-T15:38:57Z")
                        ])
    anso = mzqc_lib.AnalysisSoftware(accession="QC:9999999",
                                     name="bigwhopqc",
                                     version="1.2.3",
                                     uri="file:///dev/null")   # isn't requiring a uri too much?
    meta = mzqc_lib.MetaDataParameters(inputFiles=[infi],
                                       analysisSoftware=[anso], label="test_label")
    qm = mzqc_lib.QualityMetric(accession="QC:4000053", name="RT duration", value=99)
    qm2 = mzqc_lib.QualityMetric(accession="QC:4000061", name="Maximal MS2 frequency", value=999)
    qm3 = mzqc_lib.QualityMetric(accession="QC:4000055", name="MS1 quantiles RT fraction", value=9)
    rq = mzqc_lib.RunQuality(metadata=meta, qualityMetrics=[qm, qm2])
    sq = mzqc_lib.SetQuality(metadata=meta, qualityMetrics=[qm3])
    cv = mzqc_lib.ControlledVocabulary(name="QCvocab", uri="www.qc.ml")
    cv2 = mzqc_lib.ControlledVocabulary(name="TEST", uri="www.eff.off")
    mzqc = mzqc_lib.MzQcFile(version="1.0.0", runQualities=[rq],
                             setQualities=[sq], controlledVocabularies=[cv, cv2])
    # with open('tests/mzqc_lib_out.mzqc', 'w') as f:
    #     f.write("{ \"mzQC\": " + mzqc_lib.JsonSerialisable.ToJson(mzqc) + " }")

    syn_check = SyntaxCheck()
    syn_check.validate("{ \"mzQC\": " + mzqc_lib.JsonSerialisable.to_json(mzqc) + " }")

def test_SyntaxCheck_brokenAnalysisSoftware():
    infi = "tests/examples/individual-runs_brokenAnalysisSoftware.mzQC"  # test good detectin schema invalid
    with open(infi, 'r') as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    expected_error = "'version' is a required property @ [mzQC][runQualities][0][metadata][analysisSoftware][1]"
    assert(syn_val.get('schema validation',"")[:2] == [SCHEMA_VERSION_DISCLAIMER, expected_error])

def test_SyntaxCheck_creationDateNoTimezoneinfo():
    infi = "tests/examples/individual-runs_creationDateNoTimezoneinfo.mzQC"  # test good detectin schema invalid
    with open(infi, 'r') as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    expected_error = "'2020-12-01T11:56:34' is not a 'date-time' @ [mzQC][creationDate]"
    assert(syn_val.get('schema validation',"")[:2] == [SCHEMA_VERSION_DISCLAIMER, expected_error])

def test_SyntaxCheck_extraContent():
    infi = "tests/examples/individual-runs_extraJSONcontent.mzQC"  # test good detectin schema invalid, also QC:000 terms unknown
    with open(infi, 'r') as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    expected_error = "Additional properties are not allowed ('test' was unexpected) @ "
    assert(syn_val.get('schema validation',"")[:2] == [SCHEMA_VERSION_DISCLAIMER, expected_error])

def test_SyntaxCheck_noOuter():
    infi = "tests/examples/individual-runs-noOuter.json"  # No mzQC content found! no mzQC object no detectin
    with open(infi, 'r') as f:
        inpu = f.read()
        # json.loads(inpu)
    syn_val = SyntaxCheck().validate(inpu)
    print(syn_val)
    offenders = ['INFO - using schema: https://raw.githubusercontent.com/HUPO-PSI/mzQC/main/schema/mzqc_schema.json', "Additional properties are not allowed ('contactAddress', 'contactName', 'controlledVocabularies', 'creationDate', 'description', 'runQualities', 'version' were unexpected) @ ", "'mzQC' is a required property @ "]
    assert( all([x in syn_val.get('schema validation',"") for x in offenders] ))
