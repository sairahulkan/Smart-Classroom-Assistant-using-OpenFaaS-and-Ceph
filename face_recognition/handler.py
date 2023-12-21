import csv
import json
import os
import pickle
import subprocess
import urllib.parse

import boto3

import face_recognition

# AWS_ACCESS_KEY_ID_S3 = '7Q5QH75E2BIDWQNPYURV'
# AWS_SECRET_ACCESS_KEY_S3 = 'Y7ekHWFo4ksqAGtXgGr9tEUlskzHphKN9uH1A9v0'
# s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID_S3, region_name='us-east-1', endpoint_url='http://127.17.0.1:80',
#                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY_S3)
# import io
# s3.upload_fileobj(io.BytesIO(b'some text for ya boi'), "546proj3-1", "first.txt")
# response = s3.put_bucket_notification_configuration(
#     Bucket='546proj3-1',
#     NotificationConfiguration={
#         'TopicConfigurations': [
#             {
#                 'Id': 'input-notif',
#                 'TopicArn': 'arn:aws:sns:default::sentmessage',
#                 'Events': [
#                     's3:ObjectCreated:*'
#                 ],
#             },
#         ],
#     }
# )


def read_secret(name):
    with open("/var/openfaas/secrets/" + name) as f:
        return f.read().strip()


print(os.environ)

AWS_ACCESS_KEY_ID_S3 = read_secret('s3-access-key-id')
AWS_SECRET_ACCESS_KEY_S3 = read_secret('s3-secret-key')

# print(f"S3 Access Key: {AWS_ACCESS_KEY_ID_S3}")
# print(f"S3 Secret Key: {AWS_SECRET_ACCESS_KEY_S3}")


AWS_ACCESS_KEY_ID = read_secret('aws-access-key-id')
AWS_SECRET_ACCESS_KEY = read_secret('aws-secret-key')

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID_S3,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY_S3,
                  #   endpoint_url='http://127.17.0.1:80',
                  #   region_name='us-east-1'
                  )
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          #   region_name='us-east-1'
                          )
table_dynamo = dynamodb.Table('student_data')
input_bucket = "546proj3-1"
output_bucket = "546proj3output-1"
video_folder = "/tmp/"

# Function to read the 'encoding' file


def open_encoding(filename):
    file = open(filename, "rb")
    data = pickle.load(file)
    file.close()
    return data


def handle(event, context=None):
    print(event)
    print("context")
    print(context)
    if isinstance(event, str):
        if event.startswith('sh'):
            proc = subprocess.Popen(
                event.removeprefix('sh').strip(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.wait(10)
            if proc.stdout is None:
                print("stdout was empty. exit code " + proc.returncode)
            else:
                print(proc.stdout.read().decode())
            return
        event = json.loads(event)
    # Downloading video by extracting the key created in s3 bucket
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print(key)
    # os.makedirs(video_folder)
    s3.download_file(input_bucket, key, os.path.join(video_folder, key))

    # ffmpeg command
    os.system('ffmpeg -i ' + os.path.join(video_folder, key) +
              ' -r 1 ' + video_folder + 'image-%3d.jpeg' + ' -loglevel 8')

    # frame sent to facial recognition
    image_frame_face = face_recognition.load_image_file(
        os.path.join(video_folder, 'image-001.jpeg'))
    face_encoding = face_recognition.face_encodings(image_frame_face)[0]

    # match encoding
    encoding_file = '/home/app/function/encoding'
    file = open(encoding_file, "rb")
    encoding_pool = pickle.load(file)
    file.close()

    result = None
    for encoding in enumerate(encoding_pool['encoding']):
        if face_recognition.compare_faces([encoding[1]], face_encoding)[0]:
            result = encoding_pool['name'][encoding[0]]
            break

    # get student data
    student_data = table_dynamo.get_item(Key={'name': result})['Item']
    csv_name = key.split('.')[0] + '.csv'
    with open(video_folder + csv_name, mode='w') as f:
        f.write(
            f"{student_data['name']}, {student_data['major']}, {student_data['year']}")
        f.close()

    # s3 upload
    s3.upload_file(video_folder + csv_name, output_bucket, csv_name)
