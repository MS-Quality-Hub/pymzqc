__author__ = 'walzer'
import pytest  # Eeeeeeverything needs to be prefixed with test in order to be picked up by pytest, i.e. TestClass() and test_function()
import json
from jsonschema import ValidationError
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SemanticCheck import SemanticIssue
from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
import warnings
from itertools import chain

"""
    Semantic tests with pymzqc
     
    NOTE: warnings from the semantic test class (esp. those from fastobo or 
        pronto) are ignored!
"""

def test_SemanticIssue_class_basics():
    si = SemanticIssue(name="name",severity=123,message="message")
    assert(si.name=="name")
    assert(si.severity==123)
    assert(si.message=="message")

def test_SemanticIssue_class_fns():
    si = SemanticIssue(name="name",severity=123,message="message")
    assert(si._to_string()=="name" + " of severity "+ str(123) + " and message: " + "message")

def test_SemanticCheck_class_basics():
    sc = SemanticCheck(None)
    assert(sc.version == "")
    assert(sc.file_path == "")
    assert(sc.mzqc_obj == None)
    assert(sc._max_errors==0)
    assert(sc._load_local==False)
    assert(sc._keep_issues==False)
    assert(sc._exceeded_errors==False)

    # These may only exist after validation
    assert(not hasattr(sc, '_invalid_mzqc_obj'))

def test_SemanticCheck_dictfunction():
    sc = SemanticCheck(None)
    sc._max_errors = 2
    sc["test"] = [1]
    assert(sc["test"]==[1])

    with pytest.raises(KeyError) as dictacc:  
        sc["fail"]
    assert(str(dictacc.value) == "'fail'") 

    sc.raising("test",2)
    assert(sc["test"]==[1,2])

    with pytest.raises(ValidationError) as dictacc:  
        sc.raising("test",3)
    assert(str(dictacc.value) == "Maximum number of semantic errors incurred (2 < 4), aborting!") 

    assert(sc._exceeded_errors)

def test_SemanticCheck_clearfunction():
    sc = SemanticCheck(None)
    sc["test"] = [1]
    sc.raising("test",2)
    assert(sc["test"]==[1,2])
    sc._exceeded_errors=True
    sc.clear()
    with pytest.raises(KeyError) as dictacc:  
        sc["test"]
    assert(str(dictacc.value) == "'test'") 
    assert(not sc._exceeded_errors) 

def test_SemanticCheck_maxerrorsfunction():
    infi = "tests/examples/individual-runs_tripallsemanticchecks.mzQC"
    with open(infi, 'r') as f:
        mzqcobject = mzqc_io.FromJson(f)

    assert(type(mzqcobject) == mzqc_file)
    removed_items = list(filter(lambda x: not (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    mzqcobject.controlledVocabularies = list(filter(lambda x: (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))

    with pytest.raises(ValidationError) as dictacc:  
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sc2 = SemanticCheck(mzqc_obj=mzqcobject, file_path=infi)
            sc2.validate(load_local=True, max_errors=2)
    assert(str(dictacc.value) == "Maximum number of semantic errors incurred (2 < 4), aborting!")        
    # print(json.dumps(sc2.string_export(), sort_keys=True, indent=4))

def test_SemanticCheck_exportfunction():
    sc1 = SemanticCheck(None)
    sc1._invalid_mzqc_obj=True
    assert(sc1.string_export()=={"general": "incompatible object given to validation"})

    infi = "tests/examples/individual-runs.mzQC"  # success test
    with open(infi, 'r') as f:
        mzqcobject = mzqc_io.FromJson(f)

    assert(type(mzqcobject) == mzqc_file)
    removed_items = list(filter(lambda x: not (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    mzqcobject.controlledVocabularies = list(filter(lambda x: (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sc2 = SemanticCheck(mzqc_obj=mzqcobject, file_path=infi)
        sc2.validate(load_local=True)
    # print(json.dumps(sc2.string_export(), sort_keys=True, indent=4))
    assert(sc2.string_export() == {k: [i._to_string() for i in v] for k,v in sc2.items()})

def test_SemanticCheck_class_validation_None():
    sc = SemanticCheck(None)
    sc.validate()
    # Test invalid files are caught
    assert(sc._invalid_mzqc_obj)

def test_SemanticCheck_validation_trip_all():
    infi = "tests/examples/individual-runs_tripallsemanticchecks.mzQC"
    with open(infi, 'r') as f:
        mzqcobject = mzqc_io.FromJson(f)

    assert(type(mzqcobject) == mzqc_file)
    removed_items = list(filter(lambda x: not (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    mzqcobject.controlledVocabularies = list(filter(lambda x: (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))

    nocol = next(iter(list(filter(lambda x: x.accession=="MS:4000105", mzqcobject.runQualities[1].qualityMetrics))))
    nocol.value["MS:1000927"] = "zorg"
    mzqcobject.runQualities[1].qualityMetrics.append(nocol)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sm = SemanticCheck(mzqcobject, file_path=infi)
        sm.validate(load_local=True)
        sem_val = sm.string_export()
        
    # Test export creates as many issues as the object holds
    assert(len(list(chain.from_iterable(sem_val.values())))==len(list(chain.from_iterable(sm.values()))))

    # Test if issues for all categories were produced
    for issue_type_category in set(sm.keys()):
        assert(len(sm.get(issue_type_category,list()))>0)

    # Test invalid files are caught
    doc = SemanticCheck(None, file_path="")
    doc._document_collected_issues()
    assert(all([len(x)==0 for x in doc.values()]))
    
    # Register all issues available
    doc = SemanticCheck(mzqc_file(), file_path="")
    doc._document_collected_issues()

    # Test no documented issues have the same name
    assert(len({s.name for s in chain.from_iterable(doc.values())}) ==
            len([s.name for s in chain.from_iterable(doc.values())]))

    # Test no undocumented issue types were generated
    assert(set(sm.keys()).issubset(set(doc.keys())))

    # Test no undocumented issues were generated
    assert({s.name for s in chain.from_iterable(sm.values())}).issubset(
            {s.name for s in chain.from_iterable(doc.values())})

    # Test all documented issues were tripped
    assert({s.name for s in chain.from_iterable(sm.values())} ==
            {s.name for s in chain.from_iterable(doc.values())})  

def test_SemanticCheck_validation_success():
    infi = "tests/examples/individual-runs.mzQC"  # success test
    with open(infi, 'r') as f:
        mzqcobject = mzqc_io.FromJson(f)

    assert(type(mzqcobject) == mzqc_file)
    removed_items = list(filter(lambda x: not (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    mzqcobject.controlledVocabularies = list(filter(lambda x: (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sem_val = SemanticCheck(mzqc_obj=mzqcobject, file_path=infi)
        sem_val.validate(load_local=True)

    # print(json.dumps(sem_val.string_export(), sort_keys=True, indent=4))
    for issue_type_category in sem_val.keys():
        assert(len(sem_val.get(issue_type_category,list()))==0)
    