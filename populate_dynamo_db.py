import json
import time

import boto3

data = json.load(open('student_data.json'))
dynamodb = boto3.client('dynamodb')


response = dynamodb.create_table(AttributeDefinitions=[
    {
        'AttributeName': 'name',
        'AttributeType': 'S'
    }
],
    TableName='student_data',
    KeySchema=[
        {
            'AttributeName': 'name',
            'KeyType': 'HASH'
        },
],
    BillingMode='PROVISIONED',
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
}
)

time.sleep(30)

for e in data:
    e["id"] = {"N": str(e["id"])}
    e["name"] = {"S": e["name"]}
    e["major"] = {"S": e["major"]}
    e["year"] = {"S": e["year"]}

for e in data:
    response = dynamodb.put_item(TableName='student_data', Item=e)
