__author__ = "walzer"
import pytest  # Eeeeeeverything needs to be prefixed with test ito be picked up by pytest, i.e. TestClass() and test_function()
from mzqc import MZQCFile as qc
import numpy as np
from datetime import datetime

"""
Unit tests for the MZQCFile library
"""

# String comparison -as in TestSerialisation- needs the 'empty' attributes, too, whereas Object comparison -as in TestDeserialisation- only compares 'non-empty' attributes
QM = '{"accession": "QC:4000053", "name": "RT duration", "value": 99}'
CV = '{"name": "TEST", "uri": "www.eff.off"}'
CVT = '{"accession": "TEST:123", "name": "testname", "value": 99}'
ANSO = '{"accession": "QC:9999999", "name": "bigwhopqc", "version": "1.2.3", "uri": "file:///dev/null"}'
INFI = '{"location": "file:///dev/null", "name": "file.raw", "fileFormat": {"accession": "MS:1000584", "name": "mzML format"}, "fileProperties": [{"accession": "MS:1000747", "name": "completion time", "value": "2017-12-08-T15:38:57Z"}]}'
META = '{"label": "test_metadata", "inputFiles": [{"location": "file:///dev/null", "name": "file.raw", "fileFormat": {"accession": "MS:1000584", "name": "mzML format"}, "fileProperties": [{"accession": "MS:1000747", "name": "completion time", "value": "2017-12-08-T15:38:57Z"}]}], "analysisSoftware": [{"accession": "QC:9999999", "name": "bigwhopqc", "version": "1.2.3", "uri": "file:///dev/null"}]}'
RUQU = '{"metadata": {"label": "test_metadata", "inputFiles": [{"location": "file:///dev/null", "name": "file.raw", "fileFormat": {"accession": "MS:1000584", "name": "mzML format"}, "fileProperties": [{"accession": "MS:1000747", "name": "completion time", "value": "2017-12-08-T15:38:57Z"}]}], "analysisSoftware": [{"accession": "QC:9999999", "name": "bigwhopqc", "version": "1.2.3", "uri": "file:///dev/null"}]}, "qualityMetrics": [{"accession": "QC:4000053", "name": "RT duration", "value": 99}]}'
SEQU = '{"metadata": {"label": "test_metadata", "inputFiles": [{"location": "file:///dev/null", "name": "file.raw", "fileFormat": {"accession": "MS:1000584", "name": "mzML format"}, "fileProperties": [{"accession": "MS:1000747", "name": "completion time", "value": "2017-12-08-T15:38:57Z"}]}], "analysisSoftware": [{"accession": "QC:9999999", "name": "bigwhopqc", "version": "1.2.3", "uri": "file:///dev/null"}]}, "qualityMetrics": [{"accession": "QC:4000053", "name": "RT duration", "value": 99}]}'
NPQM = '{"accession": "QC:123", "name": "einszweidrei", "value": {"np": [0.1111111119389534, 0.25, 0.4285714328289032]}}'

cvt = qc.CvParameter(accession="TEST:123", name="testname", value=99)
infi = qc.InputFile(
    name="file.raw",
    location="file:///dev/null",
    file_format=qc.CvParameter("MS:1000584", "mzML format"),
    file_properties=[
        qc.CvParameter(
            accession="MS:1000747", name="completion time", value="2017-12-08-T15:38:57Z"
        )
    ],
)
anso = qc.AnalysisSoftware(
    accession="QC:9999999", name="bigwhopqc", version="1.2.3", uri="file:///dev/null"
)  # isn't requiring a uri a bit too much?
meta = qc.MetaDataParameters(
    input_files=[infi], analysis_software=[anso], label="test_metadata"
)
qm = qc.QualityMetric(accession="QC:4000053", name="RT duration", value=99)
rq = qc.RunQuality(metadata=meta, quality_metrics=[qm])
sq = qc.SetQuality(metadata=meta, quality_metrics=[qm])
cv = qc.ControlledVocabulary(name="TEST", uri="www.eff.off")
mzqc = qc.MzQcFile(
    version="1.0.0",
    description="pytest-test file",
    run_qualities=[rq],
    set_qualities=[sq],
    controlled_vocabularies=[cv],
)


class TestSerialisation:
    def test_ControlledVocabulary(self):
        assert qc.JsonSerialisable.to_json(cv, complete=False) == CV

    def test_CvParameter(self):
        assert qc.JsonSerialisable.to_json(cvt, complete=False) == CVT

    def test_AnalysisSoftware(self):
        assert qc.JsonSerialisable.to_json(anso, complete=False) == ANSO

    def test_InputFile(self):
        assert qc.JsonSerialisable.to_json(infi, complete=False) == INFI

    def test_MetaDataParameters(self):
        assert qc.JsonSerialisable.to_json(meta, complete=False) == META

    def test_QualityMetric(self):
        assert qc.JsonSerialisable.to_json(qm, complete=False) == QM

        # TODO more metric value types (str, float, List[float], Dict[str,float])

    def test_BaseQuality(self):
        pass

    def test_RunQuality(self):
        assert qc.JsonSerialisable.to_json(rq, complete=False) == RUQU

    def test_SetQuality(self):
        assert qc.JsonSerialisable.to_json(sq, complete=False) == SEQU

    def test_MzQcFile(self):
        # pass
        with open("/tmp/test.mzQC", "w") as f:
            f.write(qc.JsonSerialisable.to_json(mzqc, 2, complete=False))

    def test_NumpyValues(self):
        nup = qc.QualityMetric()
        nup.accession = "QC:123"
        nup.name = "einszweidrei"
        npnd = np.array([1 / 9, 2 / 8, 3 / 7], dtype=np.float32)
        nup.value = {"np": npnd}
        assert qc.JsonSerialisable.to_json(nup, complete=False) == NPQM

    def test_DateTime(self):
        try:
            zqc = qc.MzQcFile(
                version="0.1.0",
                creation_date=datetime.now().isoformat(),
                run_qualities=[],
                set_qualities=[],
                controlled_vocabularies=[],
            )
        except Exception as error:
            raise AssertionError(f"An unexpected exception {error} raised.")


# First, serialisation should be tested separately!
class TestDeserialisation:
    def test_ControlledVocabulary(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(cv)) == cv
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(cv)),
            qc.ControlledVocabulary,
        )

    def test_CvParameter(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(cvt)) == cvt
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(cvt)),
            qc.CvParameter,
        )

    def test_AnalysisSoftware(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(anso)) == anso
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(anso)),
            qc.AnalysisSoftware,
        )

    def test_InputFile(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(infi)) == infi
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(infi)), qc.InputFile
        )

    def test_MetaDataParameters(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(meta)) == meta
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(meta)),
            qc.MetaDataParameters,
        )

    def test_QualityMetric(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(qm)) == qm
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(qm)),
            qc.QualityMetric,
        )

        # TODO more metric value types (str, float, List[float], Dict[str,float])

    def test_BaseQuality(self):
        pass

    def test_RunQuality(self):
        sdrq = (qc.RunQuality)(
            **qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(rq)).__dict__
        )
        assert sdrq == rq
        assert isinstance(sdrq, qc.RunQuality)

    def test_SetQuality(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(sq)) == sq
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(sq)), qc.SetQuality
        )

    def test_MzQcFile(self):
        assert qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(mzqc)) == mzqc
        assert isinstance(
            qc.JsonSerialisable.from_json(qc.JsonSerialisable.to_json(mzqc)), qc.MzQcFile
        )
