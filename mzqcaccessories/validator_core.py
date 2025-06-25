import json
import io
import os
from typing import Union
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.MZQCFile import get_version_string
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck


def validator_combined_core(inpu: Union[io.TextIOWrapper,str], load_local:bool = True) -> dict:
    """Cross-validator shared core functionality"""   
    proto_response = dict()
    try:
        target = mzqc_io.from_json(inpu)
    except Exception:
        if isinstance(inpu, io.TextIOWrapper):
            inpu.seek(0,0)
        default_response = {"general": "No mzQC structure detectable."}
        target = json.load(inpu)
        syn_val_res = SyntaxCheck().validate(json.dumps(target))
        # older versions of the validator report a generic response in an array - return first only
        if isinstance(syn_val_res.get('schema validation', None), list):
            syn_val_res = default_response
            syn_val_res.update({'schema validation':
                                syn_val_res.get('schema validation', None)[0] if
                                syn_val_res.get('schema validation', None) else ''})
        proto_response.update(default_response)
        proto_response.update(syn_val_res)
        return proto_response

    # do syntax check first
    valt = mzqc_io.to_json(target)
    syn_val_res = SyntaxCheck().validate(valt)
    # older versions of the validator report a generic response in an array - return first only
    if isinstance(syn_val_res.get('schema validation', None), list):
        syn_val_res = {'schema validation':
                            syn_val_res.get('schema validation', None)[0] if
                            syn_val_res.get('schema validation', None) else ''}
    proto_response.update(syn_val_res)

    # do semantic checks next
    removed_items = list(filter(lambda x: not x.uri.startswith('http'), target.controlledVocabularies))
    target.controlledVocabularies = list(filter(lambda x: x.uri.startswith('http'), target.controlledVocabularies))

    sem_val = SemanticCheck(mzqc_obj=target, file_path='.')
    me = os.getenv('MAX_ERR', 0)
    if isinstance(me, str) and me.isnumeric():  # IDK if striclty necessary from getenv
        me = int(me)
    sem_val.validate(load_local=load_local, max_errors=me)
    proto_response.update(sem_val.string_export())

    # add note on removed CVs
    if removed_items:
        proto_response.update({"ontology validation":
                            ["invalid ontology URI for "+ str(it.name) for it in removed_items]})
    return proto_response
