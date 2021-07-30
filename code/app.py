import json
from decimal import Decimal

# import requests
import os
import boto3
import uuid
from pprint import pprint
from get_random_bundle import get_random

from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def uresp(msg, status=200):
    return {
        "statusCode": status,
        "body": json.dumps(msg, cls=DecimalEncoder),
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Content-Type": 'application/json'
        },
    }


hit_info_table = "generationalData"


def post_item(event, context):
    print("WE start posting item")
    if event.get("body") and isinstance(event.get("body"), str):
        body = json.loads(event["body"], parse_float=Decimal)
    else:  # we apparently in aws test
        body = event
    pprint(f"event body I got is {body}")
    if os.getenv("AWS_SAM_LOCAL"):
        ddb = boto3.resource(
            "dynamodb", endpoint_url="http://docker.for.mac.localhost:8000"
        )

    else:
        ddb = boto3.resource("dynamodb")
    table = ddb.Table(hit_info_table)
    itemId = str(uuid.uuid4())
    print('GONNA POST NEW ITEM TO DDB:', itemId)
    independent = body.get("independent", False)
    generation = body.get("generation", None)
    if independent and not generation:
        body["generation"] = 0
    new_item = table.put_item(Item={"itemId": itemId, **body})
    return {
        "statusCode": 200,
        "body": json.dumps(new_item),
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            "Content-Type": "application/json",
        },
    }


def get_list(event, context):
    pprint("I am trying to get a list of all objects in hitinfo db...")
    if os.getenv("AWS_SAM_LOCAL"):
        ddb = boto3.resource(
            "dynamodb", endpoint_url="http://docker.for.mac.localhost:8000"
        )

    else:
        ddb = boto3.resource("dynamodb")
    table = ddb.Table(hit_info_table)
    response = table.scan()
    items = response["Items"]

    return {
        "statusCode": 200,
        "body": json.dumps(items, cls=DecimalEncoder),
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }


def random_bundle(event, context):
    urlqs = event["queryStringParameters"]
    category = urlqs.get("category")
    n = int(urlqs.get("n"))
    r = {}
    if n and category:
        r = get_random(category, n)

    return {
        "statusCode": 200,
        "body": json.dumps(r, cls=DecimalEncoder),
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
    }
