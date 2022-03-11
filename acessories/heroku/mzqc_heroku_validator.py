#sudo apt update
#sudo apt install python3 python3-pip python3-flask 
#pip install Flask
#pip install git+https://github.com/MS-Quality-hub/pymzqc.git@v1.0.0
#pip install flask-restful
#pip install gunicorn

import json
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
            return {'status': 'API is running'}
        except:
            return {'status': 'API fetch was unsuccessful'}

class Validator(Resource):
    def post(self):
        default_unknown = jsonify({"general": "No mzQC structure detectable."})
        inpu = request.form.get('validator_input', None)
        try:
            target = mzqc_io.FromJson(inpu)
        except Exception as e:
            return default_unknown

        if type(target['mzQC']) != mzqc_file:
            return default_unknown
        else:
            safe = target['mzQC']
            removed_items = list(filter(lambda x: not x.uri.startswith('http'), safe.controlledVocabularies))
            safe.controlledVocabularies = list(filter(lambda x: x.uri.startswith('http'), safe.controlledVocabularies))
            print(safe)
            sem_val_res = SemanticCheck().validate(safe)
            print(sem_val_res)
            proto_response = {k: [str(i) for i in v] for k,v in sem_val_res.items()}
            proto_response.update({"unrecognised CVs": [str(it) for it in removed_items]})
            print(proto_response)
            valt = mzqc_io.ToJson(target)
            syn_val_res = SyntaxCheck().validate(valt)
            proto_response.update(syn_val_res)
            # convert val_res ErrorTypes to strings
            # add note on removed CVs
            return jsonify(proto_response)
        return default_unknown


api.add_resource(Status, '/','/status/')
api.add_resource(Validator, '/validator/')

if __name__ == '__main__':
    app.run()
