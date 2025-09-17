import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['REFERRAL_EVENTS_TABLE'])

def lambda_handler(event, context):
    try:
        # Handle both direct invocation and API Gateway proxy integration
        if 'body' in event and event['body']:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        # Extract required parameters
        event_name = body.get('event_name')
        referral_code = body.get('referral_code')
        
        # Validate required fields
        if not event_name or not referral_code:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Missing required fields: event_name and referral_code'
                })
            }
        
        # Basic input sanitization and validation
        if len(referral_code) > 100 or len(event_name) > 100:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Field values too long'
                })
            }
        
        # Only allow alphanumeric characters and common separators for referral codes
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', referral_code):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({
                    'error': 'Invalid referral code format'
                })
            }
        
        # Generate unique event ID
        event_id = str(uuid.uuid4())
        
        # Current timestamp in ISO format
        timestamp = datetime.utcnow().isoformat()
        
        # Add additional metadata for security/analytics
        user_agent = event.get('headers', {}).get('User-Agent', 'unknown') if 'headers' in event else 'unknown'
        source_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown') if 'requestContext' in event else 'unknown'
        
        # Store in DynamoDB
        table.put_item(Item={
            'event_id': event_id,
            'event_name': event_name,
            'referral_code': referral_code,
            'timestamp': timestamp,
            'user_agent': user_agent[:200],  # Truncate to prevent abuse
            'source_ip': source_ip
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Referral event recorded successfully',
                'event_id': event_id
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
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