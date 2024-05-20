import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserOffers')

def lambda_handler(event, context):
    try:
        # Parse the input data
        body = json.loads(event['body'])
        user_id = body['UserID']
        offer_name = body['OfferName']
        input_data = body['InputData']
        output_data = body['OutputData']
        
        # Check if offer already exists
        response = table.get_item(
            Key={
                'UserID': user_id,
                'OfferName': offer_name
            }
        )
        
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps(f"Offer with name {offer_name} for user {user_id} already exists.")
            }
        
        # Save the new offer
        offer_id = str(uuid.uuid4())
        table.put_item(
            Item={
                'UserID': user_id,
                'OfferID': offer_id,
                'OfferName': offer_name,
                'InputData': input_data,
                'OutputData': output_data
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Offer {offer_id} saved successfully!")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error saving offer: {str(e)}")
        }
