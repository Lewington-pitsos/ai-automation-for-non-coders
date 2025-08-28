import json
import boto3
import os
import stripe
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('${table_name}')
events_client = boto3.client('events')

stripe.api_key = os.environ.get('STRIPE_API_KEY')
webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

def lambda_handler(event, context):
    try:
        payload = event['body']
        sig_header = event['headers'].get('stripe-signature')
        
        stripe_event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        if stripe_event['type'] == 'payment_intent.succeeded':
            payment_intent = stripe_event['data']['object']
            
            response = table.scan(
                FilterExpression='stripe_payment_intent_id = :pi_id',
                ExpressionAttributeValues={':pi_id': payment_intent['id']}
            )
            
            if response['Items']:
                item = response['Items'][0]
                registration_id = item['registration_id']
                
                table.update_item(
                    Key={'registration_id': registration_id},
                    UpdateExpression='SET payment_status = :status, payment_date = :date',
                    ExpressionAttributeValues={
                        ':status': 'paid',
                        ':date': datetime.utcnow().isoformat()
                    }
                )
                
                events_client.put_events(
                    Entries=[
                        {
                            'Source': 'course.registration',
                            'DetailType': 'Payment Successful',
                            'Detail': json.dumps({
                                'registration_id': registration_id,
                                'email': item['email'],
                                'name': item['name'],
                                'payment_intent_id': payment_intent['id']
                            }),
                            'EventBusName': '${event_bus_name}'
                        }
                    ]
                )
                
                logger.info(f"Payment successful for registration: {registration_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({'received': True})
        }
        
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid payload'})
        }
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid signature'})
        }
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }