import os
import json
from jsonschema import ValidationError
from flask import Flask
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS

from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck

app = Flask(__name__)
api = Api(app)
CORS(app)

class Status(Resource):
    def get(self):
        try:
            return {'status': 'API is running', 'endpoints': ['status', 'documentation', 'validator']}
        except:
            return {'status': 'API fetch was unsuccessful'}

class Documentation(Resource):
    def get(self):
        api_doc_string = """
        This is the response to the API call for `documentation`. The API call for `status` will 
        be responded with a JSON object summarising the API `status` and list of `endpoints`. The 
        API call for `validator` with a POST of a mzqc JSON object responds with a JSON object, 
        nested for each validation mode: 
        `semantic validation` and `schema validation`. For each mode, the value will be a list of 
        validation items found to not (completely) correspond to the standard format.
        """

        semantic_doc_string = """
        The value to the 'semantic validation' key is an array of checks performed 
        on the deserialised mzQC object according to the latest specification. 
        The checks are the following:
        """
        doc = SemanticCheck(mzqc_file(), file_path="")
        doc._document_collected_issues()
        semantic_doc_string = '\n'.join([semantic_doc_string]+[f"        * '{k}':\n"+
                                         '\n'.join([f"            {i._to_string()}" for i in v]) for 
                                         k,v in doc.items()])

        syntactic_doc_string = """
        The value to the 'schema validation' key is the parsed result to the JSONschema 
        validation of given file, using the current schema (unless stated otherwise).
        """
        
        return {'documentation': {'schema validation': syntactic_doc_string, 
                                  'semantic validation': semantic_doc_string, 
                                  'API doc': api_doc_string}}

class Validator(Resource):
    def post(self):
        default_unknown = jsonify({"general": "No mzQC structure detectable."})
        inpu = request.form.get('validator_input', None)
        try:
            target = mzqc_io.from_json(inpu)
        except Exception as e:
            return default_unknown

        if type(target) != mzqc_file:
            return default_unknown
        else:
            removed_items = list(filter(lambda x: not x.uri.startswith('http'), target.controlledVocabularies))
            target.controlledVocabularies = list(filter(lambda x: x.uri.startswith('http'), target.controlledVocabularies))
            me = os.getenv('MAX_ERR', 0)
            if isinstance(me, str) and me.isnumeric():
                me = int(me)
            
            sem_val = SemanticCheck(mzqc_obj=target, file_path='.')
            try:
                sem_val.validate(load_local=False, max_errors=me)
            except ValidationError as e:
                print(e)
            proto_response = sem_val.string_export()
            if removed_items:
                proto_response.update({"ontology validation": 
                                       ["invalid ontology URI for "+ str(it.name) for it in removed_items]})

            valt = mzqc_io.to_json(target)
            syn_val_res = SyntaxCheck().validate(valt)
            # older versions of the validator report a generic response in an array - return first only
            if type(syn_val_res.get('schema validation', None)) == list:
                syn_val_res = {'schema validation': syn_val_res.get('schema validation', None)[0] if syn_val_res.get('schema validation', None) else ''}
            proto_response.update(syn_val_res)

            # print(json.dumps(proto_response, indent=2, sort_keys=True))            
            return jsonify(proto_response)
        return default_unknown

api.add_resource(Status, '/','/status/')
api.add_resource(Documentation, '/documentation/')
api.add_resource(Validator, '/validator/')

if __name__ == '__main__':
    app.run()
