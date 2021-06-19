import json

# import requests
import os
import boto3
import uuid
from pprint import pprint


def post_item(event, context):
    print('WE start posting item')
    if event.get('body') and isinstance(event.get('body'), str):
        body = json.loads(event["body"])
    else: # we apparently in aws test
        body = event
    pprint(f'event body I got is {body}')
    if os.getenv("AWS_SAM_LOCAL"):
        ddb = boto3.resource(
            "dynamodb", endpoint_url="http://docker.for.mac.localhost:8000"
        )

    else:
        ddb = boto3.resource("dynamodb")
    table = ddb.Table("hitinfo")
    itemId = str(uuid.uuid4())
    new_item = table.put_item(Item={"itemId": itemId, **body})
    return {
        "statusCode": 200,
        "body": json.dumps(new_item),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Content-Type': 'application/json',
        },
    }


from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def get_list(event, context):
    pprint('I am trying to get a list of all objects in hitinfo db...')
    if os.getenv("AWS_SAM_LOCAL"):
        ddb = boto3.resource(
            "dynamodb", endpoint_url="http://docker.for.mac.localhost:8000"
        )

    else:
        ddb = boto3.resource("dynamodb")
    table = ddb.Table("hitinfo")
    response = table.scan()
    items = response["Items"]
    for i in items:
        print(i, "jopa")
    return {
        "statusCode": 200,
        "body": json.dumps(items, cls=DecimalEncoder),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
    }
