import json
import io
import click
from mzqc.MZQCFile import get_version_string
from mzqcaccessories.validator_core import validator_combined_core

import platform
# for windows terminal color to hopefully work
if platform.system() == 'Windows':
    import os
    os.system('color')


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
        RESET = '\033[0m' # called to return to standard terminal text color
        # BACKGROUND_BLACK = '\033[40m'
        BACKGROUND_RED = '\033[41m'
        BACKGROUND_DARK_GRAY = '\033[100m'
        BACKGROUND_ORANGE = '\033[48;2;255;165;0m'

        for l in json.dumps(proto_response, indent=4, sort_keys=True).splitlines(False):
            match l:
                case str(x) if 'INFO' in x:
                    print(l.replace('INFO', BACKGROUND_DARK_GRAY + 'INFO' + RESET))
                case str(x) if 'WARNING' in x:
                    print(l.replace('WARNING', BACKGROUND_ORANGE + 'WARNING' + RESET))
                case str(x) if 'ERROR' in x:
                    print(l.replace('ERROR', BACKGROUND_RED + 'ERROR' + RESET))
                case _:
                    print(l)

if __name__ == "__main__":
    start()
