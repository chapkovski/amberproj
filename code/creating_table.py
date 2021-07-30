import boto3

# Get the service resource.
dynamodb = boto3.resource(
    "dynamodb", endpoint_url="http://docker.for.mac.localhost:8000"
)

# Create the DynamoDB table.
table = dynamodb.create_table(
    TableName="hitinfo",
    KeySchema=[
        {"AttributeName": "itemId", "KeyType": "HASH"},
    ],
    AttributeDefinitions=[
        {"AttributeName": "itemId", "AttributeType": "S"},
    ],
    BillingMode='PAY_PER_REQUEST'
)

# Wait until the table exists.
table.meta.client.get_waiter("table_exists").wait(TableName="hitinfo")

# Print out some data about the table.
print(table.item_count)
