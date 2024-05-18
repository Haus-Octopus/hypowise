import json
import boto3
import uuid

dynamodb = boto3.resource('dynamodb')
table_name = "UserOffers"

def lambda_handler(event, context):
    try:
        # Parse the body from the API Gateway event
        body = json.loads(event["body"])
        user_id = body['UserID']
        offer_name = body['OfferName']
        input_data = body['InputData']
        output_data = body['OutputData']

        offer_id = str(uuid.uuid4())  # Generate a unique OfferID

        table = dynamodb.Table(table_name)
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