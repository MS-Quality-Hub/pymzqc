import json
import io
import click
from mzqc.MZQCFile import get_version_string
from mzqcaccessories.validator_core import validator_combined_core

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
    proto_response = validator_combined_core(inpu, load_local=True)

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
