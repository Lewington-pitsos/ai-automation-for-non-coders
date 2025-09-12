import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
from meta_conversions_api import handle_contact

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SES client
ses_client = boto3.client('ses')

def lambda_handler(event, context):
    """
    Handle contact form submissions by sending emails via SES
    """
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    try:
        # Handle OPTIONS request for CORS
        if event['httpMethod'] == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Parse the request body
        if 'body' not in event or not event['body']:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing request body'})
            }
        
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
        
        # Validate required fields
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not body.get(field) or not body[field].strip():
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Extract contact data
        name = body['name'].strip()
        sender_email = body['email'].strip()
        phone = body.get('mobile', '').strip() if body.get('mobile') else ''
        message = body['message'].strip()
        
        # Get environment variables
        contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
        admin_email = os.environ.get('ADMIN_EMAIL')
        
        if not contact_form_email or not admin_email:
            logger.error("Missing required environment variables")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Server configuration error'})
            }
        
        # Compose email subject and body
        subject = f"[Website Contact - DO NOT REPLY] Message from {name}"
        
        email_body = f"""
New Contact Form Submission

Name: {name}
Email: {sender_email}
{f"Phone: {phone}" if phone else ""}
Message:
{message}

---
This is an automated message sent via the contact form on the AI Automation Mastery website.
To reply to this inquiry, please email directly to: {sender_email}
DO NOT REPLY to this email - replies will not be received.
"""
        
        # Send email via SES
        try:
            response = ses_client.send_email(
                Source=contact_form_email,
                Destination={
                    'ToAddresses': [admin_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': email_body,
                            'Charset': 'UTF-8'
                        }
                    }
                },
                ReplyToAddresses=[sender_email]
            )
            
            logger.info(f"Email sent successfully. MessageId: {response['MessageId']}")
            
            # Send Contact event to Meta Conversions API
            try:
                user_agent = event.get("headers", {}).get("User-Agent", "")
                user_data = {
                    "email": sender_email,
                    "client_user_agent": user_agent
                }
                if phone:
                    user_data["phone"] = phone
                
                # Get the source URL from the event if available
                event_source_url = event.get("headers", {}).get("referer") or event.get("headers", {}).get("Referer")
                
                meta_result = handle_contact(user_data, event_source_url)
                if meta_result["success"]:
                    logger.info(f"Meta Conversions API Contact event sent successfully for {sender_email}")
                else:
                    logger.warning(f"Failed to send Meta Conversions API Contact event for {sender_email}, error: {meta_result.get('error')}")
            except Exception as meta_error:
                logger.error(f"Error sending Meta Conversions API Contact event: {str(meta_error)}")
                # Don't fail the contact form if Meta API fails
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Contact form submitted successfully',
                    'messageId': response['MessageId']
                })
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            logger.error(f"SES error: {error_code} - {error_message}")
            
            if error_code == 'MessageRejected':
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Email address not verified or invalid'})
                }
            else:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({'error': 'Failed to send email'})
                }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }