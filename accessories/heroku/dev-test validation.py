# dev-test validation
from flask import Flask
from flask import Flask, jsonify, flash, redirect, url_for, request
from werkzeug.utils import secure_filename
from flask_restful import Resource, Api
from flask_cors import CORS

import json
from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck

# temporarily ln -s /home/walzer/psi/mzQC-development/doc/examples tests/examples
testfiles = ["tests/examples/individual-runs.mzQC",
"tests/examples/metabo-batches.mzQC",
"tests/examples/Mtb-120-outlier-metrics.mzqc",
"tests/examples/QC2-sample-example.mzQC",
"tests/examples/set-of-runs.mzQC",
"tests/examples/USI-nativeID-example.mzQC"]

# #https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
# def upload_file():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file']
#         # If the user does not select a file, the browser submits an
#         # empty file without a filename.
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('download_file', name=filename))
#     return "blablabla"


import json
from mzqc.MZQCFile import MzQcFile as mzqc_file
from mzqc.MZQCFile import JsonSerialisable as mzqc_io
from mzqc.SemanticCheck import SemanticCheck
from mzqc.SyntaxCheck import SyntaxCheck

# infi = "tests/examples/individual-runs.mzQC"  # success test
# infi = "tests/examples/individual-runs-no-outer.json"  # No mzQC content found! no mzQC object no detectin
# infi = "tests/examples/individual-runs_extraJSONcontent.mzQC"  # test good detectin schema invalid, also QC:000 terms unknown
# infi = "tests/examples/individual-runs_tableExtraColumn.mzQC"  # test good detectin
# infi = "tests/examples/individual-runs_wrongTermName.mzQC"  # test good detectin
# infi = "tests/examples/individual-runs_tableIncomplete.mzQC"  # test good detectin
# infi = "tests/examples/individual-runs_brokenAnalysisSoftware.mzQC"  # test good detectin schema invalid
# infi = "tests/examples/individual-runs_unequalTableCols.mzQC"  # test good detection
# infi = "tests/examples/individual-runs_duplicateMetric.mzQC"  # test good detection
infi = "tests/examples/individual-runs_non-metric-term.mzQC"  # test good detection

with open(infi, 'r') as f:
    inpu = f.read()
# input from web validator comes in as a js dumps() equivalent

try:
    mzqcobject = mzqc_io.FromJson(inpu)
    print("Found mzQC content, successfully loaded!")
except Exception as e:
    print("No mzQC content found!")
    try:
        json.loads(inpu)
        dummy = "mzQC-incompatible JSON"
        # dummy = json.loads(inpu)
        # print("Found json content, loading failed!")
        # print("did you forget the outer 'mzQC' JSON element?")
    except:
        # print("Unknown content, stop!")
        ret = {'schema': 'abort due to unknown content', 'semantics': {'validation': 'abort due to unknown content'}}
        #return jsonify(ret)

ret = SyntaxCheck().validate(inpu)
if type(mzqcobject) == mzqc_file:
    removed_items = list(filter(lambda x: not (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    mzqcobject.controlledVocabularies = list(filter(lambda x: (x.uri.startswith('http') or x.uri.startswith('file://')), mzqcobject.controlledVocabularies))
    sem_val = {'semantic validation': SemanticCheck().validate(mzqcobject, load_local=True)}
    sem_val.update({'invalid ontology URIs': ' , '.join([str(x) for x in removed_items])})
else:
    sem_val = {'semantic validation': {'validation': 'abort due to mzQC-incompatible JSON'}}
ret.update(sem_val)
#return jsonify(ret)
print(json.dumps(ret, indent=2, sort_keys=True))




# SyntaxCheck().validate(json.dumps(purejson))['schema'][0].partition('\n')[0]  # old version of SyntaxChecker

