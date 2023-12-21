# /usr/bin/env python3
import json
import os
import urllib.parse

import boto3
from flask import Flask, jsonify, request

HOST_IP = "192.168.49.1"
PORT = 5000
AWS_ACCESS_KEY_ID_S3 = os.getenv('AWS_ACCESS_KEY_ID_S3')
AWS_SECRET_ACCESS_KEY_S3 = os.getenv('AWS_SECRET_ACCESS_KEY_S3')
RGW_URL = os.getenv('RGW_URL')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

OUTPUT_BUCKET = '546proj3output-1'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID_S3,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY_S3,
                  region_name=AWS_DEFAULT_REGION,
                  endpoint_url=RGW_URL)

CSV_DIR = "/tmp/csv"

if not os.path.isdir(CSV_DIR):
    os.makedirs(CSV_DIR)


app = Flask(__name__)


@app.route('/print_output_bucket', methods=["POST"])
def print_output_bucket():
    if request.is_json:
        event = request.json
    else:
        event = json.loads(request.data) if request.data else request.form
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    s3.download_file(OUTPUT_BUCKET, key, os.path.join(CSV_DIR, key))
    with open(os.path.join(CSV_DIR, key)) as f:
        content = f.read()
    print(f"{key}: {content}")
    return jsonify({"key": key, "content": content})


app.run(host=HOST_IP, port=PORT, debug=True)
