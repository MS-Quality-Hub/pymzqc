__author__ = 'bittremieux, walzer'
import json
import os
import urllib.request
from typing import Dict, List, Union

import jsonschema
#from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError

class SyntaxCheck(object):
    def __init__(self, version: str="1.0.0"):
        self.version = version  
        # with open('tests/schema.json', 'r') as s:
        #    self.schema = json.loads(s.read())
        # self.schema_url = 'https://raw.githubusercontent.com/HUPO-PSI/mzQC/' \
        #             'v{v}/schema/mzqc_schema.json'.format(v=version)  
        # TODO the URI should go into the config.ini
        # TODO the versions should be available via the github branches
        self.schema_url = 'https://raw.githubusercontent.com/HUPO-PSI/mzQC/' \
                      'main/schema/mzqc_schema.json'.format(v=version)
        with urllib.request.urlopen(self.schema_url, timeout=2) as schema_in:
            self.schema = json.loads(schema_in.read().decode())
    
    def validate(self, mzqc_str: str):
        try:
            mzqc_json = json.loads(mzqc_str)
        except:
            #raise ValidationError("Given mzqc seems not to be a string representation of a json type.")
            return {'schema': ["Given mzqc seems not to be a string representation of a json type."]}

        try:
            jsonschema.validate(mzqc_json, self.schema, format_checker=jsonschema.FormatChecker())
        except ValidationError as e:
            return { 'schema': [str(e)] }
        return { 'schema': ['success'] }        
