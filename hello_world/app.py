import json

# import requests
import os
import boto3
import uuid
from pprint import pprint
from get_random_bundle import get_random

def post_item(event, context):
    
    if event.get('body') and isinstance(event.get('body'), str):
        body = json.loads(event["body"])
    else: # we apparently in aws test
        body = event
    
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

    return {
        "statusCode": 200,
        "body": json.dumps(items, cls=DecimalEncoder),
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
    }
def random_bundle(event, context):
    urlqs = event['queryStringParameters']
    category =  urlqs.get('category')
    n = int(urlqs.get('n'))
    r = {}
    if n and category:
        r = get_random(category,n)

    return {
    "statusCode": 200,
    "body": json.dumps(r,cls=DecimalEncoder),
    'headers': {
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    },
}