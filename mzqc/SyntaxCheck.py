__author__ = 'bittremieux, walzer'
import json
import os
import urllib.request
from typing import Dict, List, Union

import jsonschema
#from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

class SyntaxCheck(object):
    """
    SyntaxCheck class for syntax validations of mzQC objects (after JSON dump)

    Using member function validate of the SytnaxCheck class, mzQC objects can 
    be checked for correct syntax in its built-in serialisation.
    The result dict object from schema validation is compatible with the result
    dict object from semantic validation of the SemanticCheck class.
    """
    def __init__(self, version: str="main"):
        """
        __init__ default function, essential to instantiate the object with the
        correct version of the mzQC schema to validate with. 

        The (default) value to the version parameter will decide which version
        is chosen from the GitHub repository to validate any files. 
        The parameter value should correspond to a branch or (release) tag name
        as it exists in the repository. There, the schema is expected to be 
        located at `/schema/mzqc_schema.json`. The naming convention of regular
        branches or tags is `vMINOR.Major.MINOR.PATCH` with `v` indicating a 
        regularly versioned branch or tag. Other names are to be treated as 
        experimental but should work with the SyntaxCheck class. One exception
        is (the default value) `main` which points to the tip of the main 
        development branch.

        Parameters
        ----------
        version : str, optional
            _description_, by default "main"
        """        
        self.version = version  
        # with open('tests/schema.json', 'r') as s:
        #    self.schema = json.loads(s.read())
        # self.schema_url = 'https://raw.githubusercontent.com/HUPO-PSI/mzQC/' \
        #             'v{v}/schema/mzqc_schema.json'.format(v=version)  
        # TODO the URI should go into a config.ini
        self.schema_url = 'https://raw.githubusercontent.com/HUPO-PSI/mzQC/' \
                        + '{branch}/schema/mzqc_schema.json'.format(branch=version)
        with urllib.request.urlopen(self.schema_url, timeout=2) as schema_in:
            self.schema = json.loads(schema_in.read().decode())

    def validate(self, mzqc_str: str):
        """
        The validation function validates the given json string representation 
        against the class objects set schema (see __init__) with 
        jsonschema.validate and jsonschema.FormatChecker (default arguments).

        Parameters
        ----------
        mzqc_str : str
            The json object to be validated in string representation.

        Returns
        -------
        dict
            Returns a dictionary with key 'schema validation', containing a 
            truncated error message or in the absence of an error 'success', 
            both string type.
        """        
        try:
            mzqc_json = json.loads(mzqc_str)
        except:
            #raise ValidationError("Given mzqc seems not to be a string representation of a json type.")
            return {'schema validation': "Given mzqc seems not to be a string representation of a json type."}

        try:
            jsonschema.validate(mzqc_json, self.schema, format_checker=jsonschema.FormatChecker())
        except ValidationError as e:
            try:
                #res = "{} # {}".format(e.message, e.json_path )  # not what ValidationError doc says
                res = e.message.partition('\n')[0] + ' @ ' + ''.join('[{}]'.format(k) for k in e.path )
            except:
                res = str(e)
            return { 'schema validation': res }
        return { 'schema validation': 'success' }        
