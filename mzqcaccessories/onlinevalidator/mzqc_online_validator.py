import argparse

try:
    from flask import Flask, jsonify, request
    from flask_restful import Resource, Api
    from flask_cors import CORS
except ImportError as err:
    raise ImportError(
        "The mzQC online validator requires extra dependencies. "
        "Please install them using: pip install pymzqc[onlinevalidator]"
    ) from err

from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import get_version_string
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck
from mzqcaccessories.validator_core import validator_combined_core

app = Flask(__name__)
api = Api(app)
CORS(app)

class Status(Resource):
    """flask_restful endpoint for the status of the API"""
    def get(self):
        """GET method for the status endpoint"""

        try:
            return {'status': 'API is running', 'endpoints': ['status', 'documentation', 'validator']}
        except:
            return {'status': 'API fetch was unsuccessful'}

class Documentation(Resource):
    """flask_restful endpoint for the API self-documentation"""
    def get(self):
        """GET method for the documentation endpoint"""

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
                                  'API doc': api_doc_string, 
                                  'version': f"v{get_version_string()}-online"}}

class Validator(Resource):
    """flask_restful endpoint for the validator functionality of the API"""
    def post(self):
        """POST method for the validator endpoint"""
        inpu = request.form.get('validator_input', None)
        proto_response = validator_combined_core(inpu, load_local=False)

        proto_response["validator software"] = f"v{get_version_string()}-offline"
        return jsonify(proto_response)

api.add_resource(Status, '/','/status/')
api.add_resource(Documentation, '/documentation/')
api.add_resource(Validator, '/validator/')


def main(argv=None):
    """Run the validator API with Flask's built-in server.

    For production deployments use a WSGI server, e.g.
    ``gunicorn mzqcaccessories.onlinevalidator.mzqc_online_validator:app``.
    """
    parser = argparse.ArgumentParser(
        prog='mzqc-onlinevalidator',
        description='Serve the mzQC validator API.')
    parser.add_argument('--host', default='127.0.0.1', help='interface to bind (default: %(default)s)')
    parser.add_argument('--port', type=int, default=5000, help='port to listen on (default: %(default)s)')
    args = parser.parse_args(argv)
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
