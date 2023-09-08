import json
import click
from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck

def validate(inpu):
        default_unknown = {"general": "No mzQC structure detectable."}
        try:
            target = mzqc_io.FromJson(inpu)
        except Exception as e:
            return default_unknown

        if type(target) != mzqc_file:
            return default_unknown
        else:
            removed_items = list(filter(lambda x: not x.uri.startswith('http'), target.controlledVocabularies))
            target.controlledVocabularies = list(filter(lambda x: x.uri.startswith('http'), target.controlledVocabularies))
            sem_val_res = SemanticCheck().validate(target)
            #print(sem_val_res)
            
            proto_response = {k: [str(i) for i in v] for k,v in sem_val_res.items()}
            proto_response.update({"unrecognised CVs": [str(it) for it in removed_items]})
            #print(proto_response)
            valt = mzqc_io.ToJson(target)
            syn_val_res = SyntaxCheck().validate(valt)
            # older versions of the validator report a generic response in an array - return first only
            if type(syn_val_res.get('schema validation', None)) == list:
                syn_val_res = {'schema validation': syn_val_res.get('schema validation', None)[0] if syn_val_res.get('schema validation', None) else ''}
            proto_response.update(syn_val_res)

            # convert val_res ErrorTypes to strings
            # add note on removed CVs
            return proto_response
        return default_unknown

@click.command()  # no command necessary if it's the only one 
@click.option('-j','--write-to-file', required=False, type=click.Path(), default=None, help="File destination for the output of the validation result.")
@click.argument('input', type=click.File('r'))
def start(input, write_to_file):
    proto_response = validate(input)
    if write_to_file:
        with open(write_to_file, 'w') as f:
            json.dump(proto_response, f)
    else:
        print(json.dumps(proto_response, indent=4, sort_keys=True))            


if __name__ == "__main__":
    start()