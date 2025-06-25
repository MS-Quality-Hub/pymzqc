import json
import io
import click
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.MZQCFile import get_version_string
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck

def validate(inpu: io.TextIOWrapper) -> dict:
    """top-level function to validate mzqc input

    Calls on SemanticCheck and SyntaxCheck functionality of the pymzqc library

    Parameters
    ----------
    inpu : io.TextIOWrapper
        Input is assumed to be a a file of JSON content, other input fails validation

    Returns
    -------
    JSON
        Response structure is a dict of general, schema validation, 
        ontology validation, or categories of semantic validation
    """
    proto_response = dict()

    try:
        target = mzqc_io.from_json(inpu)
    except Exception:
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
    sem_val.validate(load_local=True)
    proto_response.update(sem_val.string_export())

    # add note on removed CVs
    if removed_items:
        proto_response.update({"ontology validation":
                            ["invalid ontology URI for "+ str(it.name) for it in removed_items]})

    return proto_response


@click.command()  # no command necessary if it's the only one
@click.version_option(f"v{get_version_string()}-offline")
@click.option('-j','--write-to-file', required=False, type=click.Path(), default=None, help="File destination for the output of the validation result.")
@click.argument('infile', type=click.File('r'))
def start(infile, write_to_file):
    proto_response = validate(infile)
    proto_response["validator software"] = f"v{get_version_string()}-offline"
    if write_to_file:
        with open(write_to_file, 'w') as f:
            json.dump(proto_response, f)
    else:
        print(json.dumps(proto_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    start()
