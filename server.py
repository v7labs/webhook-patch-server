from flask import Flask, request, jsonify
import os
import json
from src import patch_manager, darwin_manager

app = Flask(__name__)

if not "V7_KEY" in os.environ:
    raise KeyError("Could not find environment variable 'V7_KEY', add it before starting the server")

API_KEY = os.environ["V7_KEY"]

@app.route('/', methods=['GET'])
def root_endpoint():
    return '<h1>Server Is Running! !</h1>'


@app.route("/webhook", methods=['POST'])
def patch_stage_endpoint():

    with open("/app/log/request.json", 'w+') as jf:
        json.dump(request.json, jf)

    json_request = request.json
    target_dataset = request.args.get('target')

    
    target_slug = darwin_manager.parse_slug(json_request, target_dataset)
 
    try:
        assert API_KEY is not None, "Api key is None, please specify env variable 'API_KEY' before running the docker"
        folder_path = patch_manager.parse_request(json_request)
        darwin_manager.upload_data(folder_path, API_KEY, target_slug)
        patch_manager.clean_up(folder_path)
 
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    except Exception as e:
        print(e)
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'}
   
 