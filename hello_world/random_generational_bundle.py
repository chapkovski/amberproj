import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key, Attr
import params
import random
from pprint import pprint
from app import uresp, DecimalEncoder
dynamodb = boto3.resource("dynamodb")


def get_bundle_by_catper(category, persona_id, generation):
    table = dynamodb.Table(params.GENERATIONAL_TABLE_NAME)
    response = table.query(
        IndexName=params.GENERATIONAL_INDEX,
        KeyConditionExpression=Key('category').eq(category)
                               & Key("persona_id").eq(persona_id),
        ReturnConsumedCapacity="TOTAL",
        FilterExpression=Key('generation').eq(generation)
    )
    print('Capacity consumed', response.get('ConsumedCapacity'))
    items = response["Items"]
    return items


def skus_by_gen(category, persona_id, generation, n):
    print("JOPA", category, persona_id, generation, n)
    candidates = get_bundle_by_catper(category, persona_id, generation)

    nums = random.sample(candidates, n)
    res = [j for i in nums for j in i.get('shoppingCart')]
    random.shuffle(res)
    return res


def obj_by_sku(sku):
    table = dynamodb.Table(params.ZERO_GENERATION_TABLE_NAME)
    response = table.query(
        IndexName=params.SINGLE_UNIT_INDEX,
        KeyConditionExpression=Key('SKU').eq(sku),
        ReturnConsumedCapacity="TOTAL",
    )
    return response.get('Items')


def objs_by_skus(skus):
    res = []
    for sku in skus:
        res.extend(obj_by_sku(sku))
    return res


def random_generational_response(event, context):
    urlqs = event["queryStringParameters"]
    category = urlqs.get("category")
    persona_id = int(urlqs.get("persona_id"))
    generation = int(urlqs.get("generation"))
    n = int(urlqs.get("n"))

    skus = skus_by_gen(category, persona_id, generation, n)
    objs = objs_by_skus(skus)
    return uresp(objs)


if __name__ == '__main__':
    print(skus_by_gen( 'Fruit',1 ,0 ,1))