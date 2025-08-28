import json
import boto3
import uuid
from datetime import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('${table_name}')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        
        registration_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'registration_id': registration_id,
            'email': body['email'],
            'name': body['name'],
            'phone': body.get('phone', ''),
            'payment_status': 'pending',
            'registration_date': timestamp,
            'stripe_payment_intent_id': body.get('payment_intent_id', ''),
        }
        
        table.put_item(Item=item)
        
        logger.info(f"Registration created: {registration_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Registration successful',
                'registration_id': registration_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error creating registration: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }