import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key, Attr


def get_random(category, n):

    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("raw")
    r = uuid4()
    response = table.query(
        KeyConditionExpression=Key("Caboodle Category").eq(category)
        & Key("item_id").gt(r.int >> 64),
        Limit=n,
        ReturnConsumedCapacity="TOTAL",
    )
    print('Capacity consumed', response.get('ConsumedCapacity'))
    items = response["Items"]
    return items
