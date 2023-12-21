import os

import boto3

AWS_ACCESS_KEY_ID_S3 = os.getenv('AWS_ACCESS_KEY_ID_S3')
AWS_SECRET_ACCESS_KEY_S3 = os.getenv('AWS_SECRET_ACCESS_KEY_S3')
RGW_URL = os.getenv('RGW_URL')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

INPUT_BUCKET = '546proj3-1'
OUTPUT_BUCKET = '546proj3output-1'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID_S3,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY_S3,
                  region_name=AWS_DEFAULT_REGION,
                  endpoint_url=RGW_URL)
try:
    s3.create_bucket(Bucket=INPUT_BUCKET)
except:
    pass

try:
    s3.create_bucket(Bucket=OUTPUT_BUCKET)
except:
    pass


response = s3.put_bucket_notification_configuration(
    Bucket=INPUT_BUCKET,
    NotificationConfiguration={
        'TopicConfigurations': [
            {
                'Id': 'input-notif',
                'TopicArn': 'arn:aws:sns:default::sentmessage',
                'Events': [
                    's3:ObjectCreated:*'
                ],
            },
        ],
    }
)

response = s3.put_bucket_notification_configuration(
    Bucket=OUTPUT_BUCKET,
    NotificationConfiguration={
        'TopicConfigurations': [
            {
                'Id': 'output-notif',
                'TopicArn': 'arn:aws:sns:default::respondmessage',
                'Events': [
                    's3:ObjectCreated:*'
                ],
            },
        ],
    }
)
