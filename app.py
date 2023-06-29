from flask import Flask, request, jsonify, make_response
from recocr import frOCR, translate_text
import json, os
import base64
import subprocess
import sys
import pytesseract

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
#/api/recocr
# Define the function to get item_inf which is a list of json [{"item_id":  """, "item_name": ""}] PAY ATTENTION INPUT SHOULD BE USED WITH "" not ''
# csv file and model path as well as jquery are the input to the semantic search file
def recocr():#(picture#, HH_id, language):


    data = request.get_json()
    picture = data['image']
    HH_id = data['HH_id']
    language = data['language']

    # create the response data
    if language == 'fr':
        response_output = frOCR(picture,HH_id,language,frpkg_path)   # for testing commented out

    response = make_response(jsonify(response_output), 200)

    # set the CORS headers
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    #response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    
    return response


if __name__  == "__main__":

    app.run(debug=True)

