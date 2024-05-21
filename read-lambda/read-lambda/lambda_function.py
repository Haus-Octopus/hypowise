import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserOffers')

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    user_id = event['pathParameters']['user_id']
    print(f"Querying for user_id: {user_id}")  # Debug log

    try:
        response = table.query(
            KeyConditionExpression=Key('UserID').eq(user_id)
        )
        offers = response['Items']
        print(f"Offers found: {offers}")  # Debug log
        
        return {
            'statusCode': 200,
            'body': json.dumps(offers, cls=DecimalEncoder)
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error reading offers: {str(e)}")
        }
