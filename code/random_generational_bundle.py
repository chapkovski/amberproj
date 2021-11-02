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
    print('Capacity consumed by get_bundle_by_catper', response.get('ConsumedCapacity'))
    items = response["Items"]
    return items


def get_bundle_by_cat_exl_per(category, persona_id, generation):
    table = dynamodb.Table(params.GENERATIONAL_TABLE_NAME)
    response = table.query(
        IndexName='category-generation-index',
        KeyConditionExpression=Key('category').eq(category) & Key("generation").eq(generation),
        ReturnConsumedCapacity="TOTAL",
        FilterExpression= Attr("persona_id").ne(persona_id)
    )
    print('Capacity consumed by get_bundle_by_cat_exl_per', response.get('ConsumedCapacity'))
    items = response["Items"]

    return items


def skus_by_gen(category, persona_id, generation, n):
    candidates = get_bundle_by_catper(category, persona_id, generation)
    how_many = min(len(candidates), n)
    nums = random.sample(candidates, how_many)
    res = [j for i in nums for j in i.get('shoppingCart')]
    res = list(set(res))
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


def single_random_bundle(category, persona_id, generation, ):
    all_others = get_bundle_by_cat_exl_per(category, persona_id, generation, )
    num = random.choice(all_others)
    res = [j for j in num.get('shoppingCart')]
    return res


def get_random_items_zero(category, n):
    table = dynamodb.Table(params.ZERO_GENERATION_TABLE_NAME)
    r = uuid4()
    response = table.query(
        KeyConditionExpression=Key("Caboodle Category").eq(category)
                               & Key("item_id").gt(r.int >> 64),
        Limit=n,
        ReturnConsumedCapacity="TOTAL",
    )
    print('Capacity consumed', response.get('ConsumedCapacity'))
    items = response["Items"]
    items = [i.get('SKU') for i in items]
    return items


def random_generational_response(event, context):
    urlqs = event["queryStringParameters"]
    category = urlqs.get("category")
    persona_id = int(urlqs.get("persona_id"))
    generation = int(urlqs.get("generation"))
    n = int(urlqs.get("n"))

    skus = skus_by_gen(category, persona_id, generation, n)
    if len(skus) < params.MIN_LENGTH:
        skus.extend(single_random_bundle(category, persona_id, generation, ))
    skus = list(set(skus))
    print(f'Plan to add: {params.MIN_LENGTH - len(skus)}')
    while len(skus) < params.MIN_LENGTH:
        rest = params.MIN_LENGTH - len(skus)
        skus.extend(get_random_items_zero(category, rest))
        skus = list(set(skus))
    objs = objs_by_skus(skus)
    unique_skus =[]
    res = []
    for i in objs:
        if i.get('SKU') not in unique_skus:
            unique_skus.append(i.get('SKU'))
            res.append(i)

    random.shuffle(res)
    return uresp(res)


if __name__ == '__main__':
    print(skus_by_gen('Fruit', 1, 0, 1))
