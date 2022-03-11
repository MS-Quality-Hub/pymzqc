__author__ = 'walzer'
import pytest  # Eeeeeeverything needs to be prefixed with test in order to be picked up by pytest, i.e. TestClass() and test_function()
import mzqc.MZQCFile as qc
from mzqc.SemanticCheck import SemanticCheck

def test_SemanticCheck():
    cvt = qc.CvParameter(accession="TEST:123", name="testname", value=99)
    infi = qc.InputFile(name="file.raw",location="file:///dev/null", 
                        fileFormat=qc.CvParameter("MS:1000584", "mzML format"), 
                        fileProperties=[qc.CvParameter(accession="MS:1000747", 
                                                        name="completion time", 
                                                        value="2017-12-08-T15:38:57Z")
                        ])
    anso = qc.AnalysisSoftware(accession="QC:9999999", name="bigwhopqc", version="1.2.3", uri="file:///dev/null")   # isn't requiring a uri a bit too much?
    meta = qc.MetaDataParameters(inputFiles=[infi],analysisSoftware=[anso], label="test_label")
    qm = qc.QualityMetric(accession="QC:4000053", name="RT duration", value=99)
    qm2 = qc.QualityMetric(accession="QC:4000061", name="Maximal MS2 frequency", value=999)
    qm3 = qc.QualityMetric(accession="QC:4000055", name="MS1 quantiles RT fraction", value=9)
    rq = qc.RunQuality(metadata=meta, qualityMetrics=[qm, qm2])
    sq = qc.SetQuality(metadata=meta, qualityMetrics=[qm3])
    cv = qc.ControlledVocabulary(name="QCvocab", uri="www.qc.ml")
    cv2 = qc.ControlledVocabulary(name="TEST", uri="www.eff.off")
    mzqc = qc.MzQcFile(version="1.0.0", runQualities=[rq], setQualities=[sq], controlledVocabularies=[cv, cv2])  
    # with open('tests/mzqc_lib_out.mzqc', 'w') as f:
    #     f.write("{ \"mzQC\": " + qc.JsonSerialisable.ToJson(mzqc) + " }")
        
    sem_check = SemanticCheck()
    sem_check.validate(mzqc) 

