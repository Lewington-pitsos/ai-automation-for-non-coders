import json
import boto3
import uuid
from datetime import datetime
import logging
import os
from meta_conversions_api import handle_complete_registration
from email_templates import get_application_confirmation_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
ses_client = boto3.client('ses')

# Get environment variables
table_name = os.environ.get("TABLE_NAME", "course_registrations")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Handle livestream registration form submissions
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
        
        # Parse request body
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
        required_fields = ['name', 'email']
        for field in required_fields:
            if not body.get(field) or not body[field].strip():
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Missing required field: {field}'})
                }
        
        # Extract data
        email = body['email'].strip().lower()
        name = body['name'].strip()
        
        # Determine request type and course ID
        registration_type = body.get('registration_type', 'livestream')
        
        if registration_type == 'application':
            course_id = '01_ai_automation_for_non_coders'
            payment_status = 'applied'
            payment_amount = 0
        else:  # livestream
            course_id = 'tax-livestream-01'
            payment_status = 'paid'
            payment_amount = 0
        
        # Check if registration already exists
        try:
            existing_item = table.get_item(
                Key={
                    'course_id': course_id,
                    'email': email
                }
            )
            
            if "Item" in existing_item:
                logger.info(f"Duplicate livestream registration attempt for email: {email}")
                return {
                    'statusCode': 409,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Registration already exists for this email'
                    })
                }
        except Exception as e:
            logger.error(f"Error checking existing registration: {str(e)}")
        
        # Create new registration
        registration_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create registration item
        item = {
            "course_id": course_id,
            "email": email,
            "registration_id": registration_id,
            "name": name,
            "payment_status": payment_status,
            "payment_amount": payment_amount,
            "registration_date": timestamp,
            "registration_type": registration_type,
            "stripe_session_id": "",  # No Stripe session
        }
        
        # Add application-specific fields if this is an application
        if registration_type == 'application':
            # Add additional fields from registration form
            item.update({
                "phone": body.get("phone", ""),
                "company": body.get("company", ""),
                "job_title": body.get("jobTitle", ""),
                "experience": body.get("experience", ""),
                "referral_source": "applied",
                "automation_interest": body.get("automationInterest", ""),
                "automation_barriers": body.get("automationBarriers", ""),
                "time_commitment": body.get("timeCommitment", ""),
                "attendance_confirmed": body.get("attendance", False),
                "consent_given": body.get("consent", False),
                "dietary_requirements": "none",
            })
        
        # Store in DynamoDB
        table.put_item(Item=item)
        logger.info(f"{registration_type.title()} created: {registration_id} for email: {email}")
        
        # Send confirmation email to user
        try:
            if registration_type == 'application':
                send_application_confirmation_email(name, email, registration_id)
                logger.info(f"Application confirmation email sent to {email}")
            else:
                send_user_confirmation_email(name, email, registration_id)
                logger.info(f"Livestream confirmation email sent to {email}")
        except Exception as email_error:
            logger.error(f"Error sending confirmation email: {str(email_error)}")
            # Don't fail the registration if email fails
        
        # Send notification to admin
        try:
            send_admin_notification(name, email, registration_id, registration_type, body if registration_type == 'application' else None)
            logger.info(f"Admin notification sent for {registration_type}: {registration_id}")
        except Exception as admin_error:
            logger.error(f"Error sending admin notification: {str(admin_error)}")
            # Don't fail the registration if admin notification fails
        
        # Send CompleteRegistration event to Meta Conversions API with livestream type
        try:
            user_agent = event.get("headers", {}).get("User-Agent", "")
            user_data = {
                "email": email,
                "client_user_agent": user_agent
            }
            
            # Get the source URL from the event if available
            event_source_url = event.get("headers", {}).get("referer") or event.get("headers", {}).get("Referer")
            
            # Pass the actual registration_type
            meta_result = handle_complete_registration(user_data, event_source_url, registration_id, registration_type=registration_type)
            if meta_result["success"]:
                logger.info(f"Meta Conversions API CompleteRegistration ({registration_type}) event sent for: {registration_id}")
            else:
                logger.warning(f"Failed to send Meta Conversions API event: {meta_result.get('error')}")
        except Exception as meta_error:
            logger.error(f"Error sending Meta Conversions API event: {str(meta_error)}")
            # Don't fail the registration if Meta API fails
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': f'{registration_type.title()} successful',
                'registration_id': registration_id
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }


def create_email_message(name, registration_id):
    subject = "Welcome to the AI Tax Automation Livestream!"

    email_body_html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #000; color: #fff; padding: 30px; text-align: center;">
<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" viewBox="0 0 2048 2048" width="150" height="150" xmlns="http://www.w3.org/2000/svg">
<path transform="translate(0)" d="m0 0h2048v2048h-2048z"/>
<path transform="translate(1557,341)" d="m0 0h16l13 4 9 5 12 11 7 7 9 11 9 10 11 14 12 14 7 9 11 14 14 17 18 22 28 34 9 11 8 10 11 13 7 9 14 17 11 14 11 13 12 16 8 12 4 11v18l-5 10-7 9-11 12-11 10-20 16-13 11-8 7-11 9-14 12-13 10-16 13-11 9-13 11-8 7-10 8-16 13-17 14-14 12-10 8-12 11-9 7-15 12-22 18-17 14-15 13-8 7-11 9-14 11-16 13-12 10-8 7-13 11-14 12-13 10-15 12-13 10-26 22-17 13-10 9-10 8-13 10-12 11-9 7-10 8-11 9-13 11-14 11-17 14-11 9-14 11-14 12-12 9-12 10-8 7-11 9-17 14-14 11-14 12-8 6-12 10h-2l-1 3-14 11-10 9-9 7-14 11-11 9-10 8-9 8-11 9-15 12-17 13-16 13-11 9-9 8-11 9-13 10-16 13-14 11-12 11-12 9-10 8-28 22-13 11-12 10-11 9-12 9-15 12-14 11-10 9-10 8-12 10-26 20-16 13-15 13-16 13-12 9-13 10-16 13-15 12-14 10-16 8-14 3h-9l-12-2-12-6-18-18-11-14-9-11-14-18-13-16-13-17-13-16-13-17-11-14-13-16-10-13-14-18-11-14-9-11-11-14-13-16-13-18-7-11-9-17-2-7 1-10 5-13 9-12 8-9 8-7 17-14 10-8 17-14 13-11 14-11 13-11 10-8 17-14 13-11 14-11 17-14 10-8 16-13 13-11 28-22 17-14 11-9 16-13 13-11 14-11 22-18 14-12 26-22 14-11 13-11 14-11 13-11 8-7 13-11 8-6 16-13 14-11 14-12 10-8 14-11 15-12 13-10 10-9 11-9 9-8 11-8 13-11 14-11 9-8 10-8 15-13 14-11 11-9 10-8 14-12 14-11 14-12 13-10 15-13 14-11 15-13 11-9 14-12 10-8 16-13 14-11 11-9 14-12 32-26 14-11 13-11 11-9 13-11 14-11 9-8 10-8 16-13 11-9 13-11 10-8 11-9 17-14 10-8 11-9 13-11 11-9 13-11 10-8 16-13 13-11 11-9 13-11 11-9 12-10 14-11 16-13 18-14 10-7 11-6 7-3z"/>
<path transform="translate(1557,341)" d="m0 0h16l13 4 9 5 12 11 7 7 9 11 9 10 11 14 12 14 7 9 11 14 14 17 18 22 28 34 9 11 8 10 11 13 7 9 14 17 11 14 11 13 12 16 8 12 4 11v18l-5 10-7 9-11 12-11 10-20 16-13 11-8 7-11 9-14 12-13 10-16 13-11 9-13 11-8 7-10 8-16 13-17 14-14 12-10 8-12 11-9 7-15 12-22 18-17 14-15 13-8 7-11 9-14 11-16 13-12 10-8 7-13 11-14 12-13 10-15 12-13 10-26 22-17 13-10 9-10 8-13 10-12 11-9 7-10 8-11 9-13 11-14 11-17 14-11 9-14 11-14 12-12 9-12 10-8 7-11 9-17 14-14 11-14 12-8 6-12 10h-2l-1 3-14 11-10 9-9 7-14 11-11 9-10 8-9 8-11 9-15 12-17 13-16 13-11 9-9 8-11 9-13 10-16 13-14 11-12 11-12 9-10 8-28 22-13 11-12 10-11 9-12 9-15 12-14 11-10 9-10 8-12 10-26 20-16 13-15 13-16 13-12 9-13 10-16 13-15 12-14 10-16 8-14 3h-9l-12-2-12-6-18-18-11-14-9-11-14-18-13-16-13-17-13-16-13-17-11-14-13-16-10-13-14-18-11-14-9-11-11-14-13-16-13-18-7-11-9-17-2-7 1-10 5-13 9-12 8-9 8-7 17-14 10-8 17-14 13-11 14-11 13-11 10-8 17-14 13-11 14-11 17-14 10-8 16-13 13-11 28-22 17-14 11-9 16-13 13-11 14-11 22-18 14-12 26-22 14-11 13-11 14-11 13-11 8-7 13-11 8-6 16-13 14-11 14-12 10-8 14-11 15-12 13-10 10-9 11-9 9-8 11-8 13-11 14-11 9-8 10-8 15-13 14-11 11-9 10-8 14-12 14-11 14-12 13-10 15-13 14-11 15-13 11-9 14-12 10-8 16-13 14-11 11-9 14-12 32-26 14-11 13-11 11-9 13-11 14-11 9-8 10-8 16-13 11-9 13-11 10-8 11-9 17-14 10-8 11-9 13-11 11-9 13-11 10-8 16-13 13-11 11-9 13-11 11-9 12-10 14-11 16-13 18-14 10-7 11-6 7-3zm-1 45-19 9-18 14-17 13-10 9-14 11-11 9-11 10-9 7-11 9-13 11-10 8-11 9-16 13-12 10-11 9-14 11-10 9-9 7-16 13-15 13-16 13-10 8-12 10-10 8-10 9-9 7-12 10-11 9-14 11-14 12-16 13-14 11-9 8-10 8-14 11-14 12-11 9-13 11-14 11-13 11-22 18-13 11-17 13-9 8-9 7-11 9-8 7-16 13-17 14-13 10-9 8-13 10-8 7-33 27-8 7-10 7-3 2v2l-4 2-9 8-8 7-14 11-12 10-14 11-11 9-17 14-13 11-14 11-15 12-8 7-12 9-9 8-9 7-14 12-12 10-11 9-16 13-11 9-10 8-14 12-11 9-10 8-11 9-16 13-14 11-9 8-11 9-14 11-15 12-11 9-14 11-15 13-10 8-16 13-28 22-14 12-9 7-14 11-12 10-9 7-13 12-4 5-3 7 1 8 4 11 7 11 12 14 9 11 11 13 10 13 7 9 12 15 22 28 7 9 10 13 10 12 9 11 10 13 10 12 13 17 9 11 8 10 13 16 13 13 9 3 8-1 12-7 13-10 14-11 12-10 11-9 13-11 11-9 15-12 17-13 15-13 9-7 10-8 9-7 14-11 13-11 22-18 12-10 17-13 13-11 10-8 14-12 16-13 13-10 16-13 9-7 28-24 11-9 13-11 12-9 16-13 26-22 10-8 28-22 16-13 14-12 10-8 12-10 14-11 13-11 9-7 14-12 11-9 13-11 9-7 14-11 13-11 11-9 13-11 11-9 16-12 11-9 14-11 10-9 10-8 13-11 14-11 13-10 13-11 14-11 22-18 13-11 11-9 16-13 14-12 17-14 12-10 14-11 16-13 13-11 10-8 14-12 10-8 16-13 13-10 14-12 15-13 8-7 13-11 13-10 17-14 22-18 17-14 14-12 12-9 16-13 13-11 10-8 13-11 17-13 14-11 12-11 10-10 3-5v-7l-8-16-6-10-11-14-11-13-13-15-14-17-9-11-11-13-9-11-12-14-9-11-11-13-10-13-13-16-11-13-9-11-14-17-11-14-11-12-8-6-8-4z" fill="#FEFEFE"/>
<path transform="translate(476,341)" d="m0 0h18l14 5 13 8 16 12 21 16 10 8 14 11 17 14 14 12 28 22 16 13 10 8 16 13 14 11 13 11 17 13 34 28 15 12 11 9 14 11 11 9 12 10 22 18 13 11 10 8 14 11 13 11 14 11 10 9 9 7 13 11 10 8 14 11 13 10 10 9 8 7 8 8-5 5-9 11-8 7-6-2-11-7-13-11-14-11-13-11-14-11-12-10-11-9-16-13-13-11-13-10-14-11-17-14-11-9-14-12-11-9-10-8-17-14-9-7-11-9-17-14-13-10-14-11-13-10-13-11-28-22-16-13-14-11-14-12-11-9-16-13-13-10-16-13-13-10-14-10-11-5h-6l-12 8-15 15-9 11-11 13-11 14-8 9-8 10-18 22-13 16-6 7-9 11-8 9-9 12-8 9-8 10-9 10-10 13-9 10-9 11-13 15-9 12-7 11-1 9 5 10 14 14 10 8 12 10 9 7 16 13 17 14 14 11 13 11 11 9 15 13 10 8 13 11 17 13 17 14 11 9 13 11 11 9 16 13 10 8 14 11 13 11 33 27 14 11 17 14 13 11 10 8 13 11 18 13 13 12 4 5-1 4-7 6-7 8-7 6-4-1-11-8-13-11-17-13-13-11-9-7-16-13-14-12-11-9-16-13-14-11-16-13-13-11-11-9-13-11-28-22-17-14-26-22-14-11-10-8-16-13-17-14-14-12-14-11-16-13-14-11-17-14-13-11-12-11-9-9-9-14-6-12v-8l6-15 12-18 9-12 14-17 11-13 8-10 9-10 8-10 13-16 18-22 12-14 11-13 14-17 10-13 11-13 8-10 11-14 12-14 22-28 11-12 11-8 9-4z" fill="#FEFEFE"/>
<path transform="translate(1385,1066)" d="m0 0 7 1 12 7 14 12 42 33 12 10 10 8 14 11 13 11 14 11 13 11 13 10 15 12 14 11 16 13 28 22 16 13 10 8 14 11 13 11 12 9 16 13 17 14 16 13 14 11 22 18 12 11 5 4 7 8 6 8 7 14 1 4v11l-5 13-9 15-13 18-21 27-11 13-11 14-14 18-10 13-11 14-12 14-9 12-13 17-10 13-9 11-11 14-9 12-10 13-9 11-10 13-11 12-5 5-9 6-9 3-6 1h-19l-13-4-9-5-16-12-28-22-25-20-22-18-17-14-13-10-14-11-17-14-10-8-16-13-14-11-10-8-16-13-22-18-17-14-13-10-13-11-10-8-13-11-14-11-16-13-14-11-12-10-14-11-13-11-14-11-16-13-17-13-13-11-11-9-7-6-2-5 6-5 8-6 5-6 4-1 11 4 11 8 13 10 14 11 13 11 11 9 10 8 17 13 13 10 10 9 11 9 16 13 17 13 12 10 13 10 14 12 14 11 9 8 17 13 16 13 12 10 11 9 14 11 16 13 14 11 14 12 14 11 17 14 13 10 12 9 11 10 11 9 12 10 17 12 16 8 8 1 9-5 11-10 8-10 10-13 9-12 10-13 10-12 12-17 10-12 22-28 10-12 7-9 11-14 9-11 7-9 13-16 13-17 11-14 12-15 8-14 1-8-11-17-11-10-28-22-13-10-17-14-10-8-14-11-13-11-13-10-17-14-56-44-17-14-16-13-17-13-13-10-14-12-10-8-16-13-13-10-14-11-16-13-9-7-17-14-15-12-8-5 1-4 6-8 9-9z" fill="#FEFEFE"/>
<path transform="translate(1265,980)" d="m0 0h6l8 6 12 15 12 16v2l4 1-2 4-9 9-11 9-26 22-10 8-8 7-17 13-13 11-9 7-13 11-11 9-13 11-12 9-14 11-13 11-11 9-13 11-15 12-17 13-10 9-10 8-14 12-22 18-14 11-16 13-14 12-11 9-14 12-12 9-14 11-9 8-14 11-7 6-11 9-16 13-12 9-15 12-10 7-5-1-8-9-18-27-2-5v-6l8-9 14-11 13-10 8-7 17-14 15-12 14-11 12-10 9-7 14-12 16-13 13-10 13-11 11-9 26-22 10-8 14-11 7-6 9-7 14-11 15-13 22-18 10-8 14-11 10-8 28-24 11-9 9-7 8-7 11-8 10-9 11-9 17-14 16-13 8-7 12-9z" fill="#FEFEFE"/>
<path transform="translate(1107,777)" d="m0 0h7l8 7 10 13 11 15 3 6v5l-4 5-10 8-13 11-13 10-12 9-10 9-11 9-10 9-13 10-10 9-14 10-13 11-16 13-9 8-9 7-15 12-8 6-34 28-13 11-17 14-11 8-13 11-22 18-13 11-11 9-13 10-11 9-10 9-20 16-11 9-12 10-11 8-7 6-6 4-4-1-12-12-9-13-9-14-2-6 10-9 8-7 13-12 11-9 13-10 11-8 16-12 11-10 8-7 13-11 16-13 13-10 14-11 8-7 14-12 11-9 12-10 17-13 11-8 11-10 8-7 17-14 22-18 14-11 10-8 12-11 11-9 14-12 14-11 10-8 14-11 14-12 16-13z" fill="#FEFEFE"/>
<path transform="translate(1592,1415)" d="m0 0 7 1 12 8 28 22 16 13 13 10 10 10 3 5-1 5-5 10-6 7-9 12-13 16-13 17-11 14-11 13-11 14-8 7-5-2-16-13-9-7-15-13-14-11-12-10-1-6 6-9 8-11 10-13 9-13 8-15 1-7-3-5-1-4 9-14 6-8 9-10 8-12z" fill="#FEFEFE"/>
<path transform="translate(610,1513)" d="m0 0 7 1 8 6 9 11 15 20 3 2-2 4-10 10-10 8-16 13-14 11-12 11-13 10-14 11-16 13-12 10-10 7-11 3-8-7-10-14-9-13-4-6 2-5 3-6 11-10 42-33 10-8 13-11 14-11 9-7 14-11z" fill="#FEFEFE"/>
<path transform="translate(1605,480)" d="m0 0 5 1 8 6 10 11 9 11 7 11 1 6-5 6-8 7-7 6-16 12-13 10-16 12-14 13-13 10-14 11-13 11-4 3-5 1-9-4-8-8-8-11-10-13-3-4 1-4 5-8 14-12 20-15 17-14 11-10 11-9 16-13 17-13 11-8z" fill="#FEFEFE"/>
<path transform="translate(1604,1313)" d="m0 0 6 2 13 10 12 10 14 11 12 10 14 11 11 9 17 13 12 10 9 7v2l4 2 4 6v7l-7 11-12 14-7 8-5 5-4 1-10-6-13-10-16-13-22-18-13-11-13-10-15-12-11-9-11-10-3-4 1-5 9-11 11-14 8-11z" fill="#FEFEFE"/>
<path transform="translate(386,544)" d="m0 0 10 4 9 7 14 11 16 13 28 22 17 14 13 10 7 6 5 6v6l-6 12-9 12-7 10-6 8-4 2-15-9-14-11-11-9-13-10-14-11-13-10-13-11-8-7-10-9-7-7-2-5 4-8 9-12 7-10 9-11z" fill="#FEFEFE"/>
<path transform="translate(536,1465)" d="m0 0h6l8 7 10 14 9 13 4 10-2 5-5 6h-2v2l-13 10-10 8-9 7-11 9-8 7-16 13-24 18-7 3h-7l-6-4-7-8-8-11-9-13-2-3 1-5 6-8 8-7 18-13 8-7 9-7 10-9 10-8 17-14 14-10z" fill="#FEFEFE"/>
<path transform="translate(1382,1465)" d="m0 0 5 1 8 4 9 7 14 10 10 9 8 6 11 9 17 14 13 11 8 6 10 9 3 2-1 4-6 10-5 6-6 9-6 7-7 9-4 1-10-6-16-12-26-20-14-11-14-12-10-8-17-14-5-7 1-4 9-10 7-10 8-12z" fill="#FEFEFE"/>
<path transform="translate(442,478)" d="m0 0 9 4 17 14 17 13 13 11 12 9 11 9 12 9 10 10 1 3-9 12-4 4-4 7-9 10-6 8-3 3-5-2-11-6-10-7-15-12-11-9-14-11-11-9-20-18-3-3-1-7 10-14 13-16 8-10z" fill="#FEFEFE"/>
<path transform="translate(459,1417)" d="m0 0 7 1 9 7 13 17 7 10 3 5-1 5-7 9-8 7-11 9-10 8-12 10-11 9-12 10-13 8-7-1-10-9-20-26-4-8 17-16 16-12 15-13 10-8 9-8 9-7 9-6z" fill="#FEFEFE"/>
<path transform="translate(1341,1107)" d="m0 0 8 1 6 4 12 9 18 14 16 13 17 13 5 5v2l4 2-1 4-6 7-9 11-10 11-7 9-5 3-5-2-14-10-14-12-10-8-15-13-14-11-11-9v-2l-2-1 4-9 10-9 10-8 8-8z" fill="#FEFEFE"/>
<path transform="translate(1142,1272)" d="m0 0h7l13 9 14 11 7 7 13 10 14 11 3 3 1 7-8 11-10 12-10 14-4 4-9-5-14-9-15-12-14-11-13-12-12-9-1-4 4-6 17-17 11-9z" fill="#FEFEFE"/>
<path transform="translate(1519,1246)" d="m0 0 6 1 10 8 13 10 14 11 11 9 8 7 2 3v6l-6 10-12 14-7 8-7 6-7-1-10-5-9-7-14-11-15-13-8-8-2-6 7-10 11-13 9-12z" fill="#FEFEFE"/>
<path transform="translate(332,611)" d="m0 0 6 1 11 7 14 12 11 9 12 9 6 5 2 3-1 5-6 5-6 8-8 10-6 7-7 8-3 1-10-5-14-10-11-9-13-12-7-6-2-6 4-10 9-13 4-6h2l2-4 5-6z" fill="#FEFEFE"/>
<path transform="translate(496,414)" d="m0 0 5 1 11 7 17 13 20 16 4 4v2h2l2 3-1 4-12 12-7 9-12 14-3 4-8-1-11-7-13-11-11-9-12-11-3-4 1-6 7-11 11-15 9-10z" fill="#FEFEFE"/>
<path transform="translate(1516,1572)" d="m0 0 6 1 11 8 11 10 13 9 11 9 6 7 2 6-6 10-11 14-13 16-6 1-6-3-13-11-10-8-7-7-13-10-3-3-2-7 6-11 10-12 10-14z" fill="#FEFEFE"/>
<path transform="translate(1639,674)" d="m0 0h6l8 7 7 10 13 18 4 6-1 4-9 9-11 9-10 8-11 9-9 7-4 2h-3l-9-11-12-16-8-11-3-8 2-4 9-9 14-11 18-14z" fill="#FEFEFE"/>
<path transform="translate(412,676)" d="m0 0 6 1 11 7 13 11 13 10 9 6 3 4v7l-9 14-9 11-7 9-8 9-6-2-11-8-15-13-11-9-9-8-3-7 1-4 6-8 10-11 10-14z" fill="#FEFEFE"/>
<path transform="translate(485,735)" d="m0 0 7 2 12 8 14 12 16 13 8 7 1 5-11 12-7 10-8 9-4 7-4 5-6-2-12-8-12-9-17-14-10-9-1-4 8-9 10-14 9-11 6-9z" fill="#FEFEFE"/>
<path transform="translate(764,1391)" d="m0 0 7 1 6 5 8 10 12 18 6 5-1 4-6 7-17 13-18 14-9 6-9 3-11-12-12-16-7-9-3-4 1-4 13-12 11-9 12-9 10-8z" fill="#FEFEFE"/>
<path transform="translate(1233,1343)" d="m0 0 7 2 11 8 14 11 13 10 7 5 4 6-1 7-8 12-10 13-11 16-5-1-11-7-9-8-12-9-13-11-7-6-1-2v-6l10-11 10-13z" fill="#FEFEFE"/>
<path transform="translate(560,796)" d="m0 0 9 3 14 11 15 12 8 6 8 7 1 4-3 8-7 10-7 8-7 10-11 11-9-6-17-13-13-11-9-7-4-9 2-5 7-11 11-12 8-12z" fill="#FEFEFE"/>
<path transform="translate(815,1124)" d="m0 0 5 2 9 7 11 13 9 11 8 9-1 5-8 8-11 9-13 11-8 6-10 6-6-1-10-11-13-17-10-13 1-5 12-11 11-9 11-10z" fill="#FEFEFE"/>
<path transform="translate(1715,612)" d="m0 0 6 2 10 8 7 8 9 13 4 10-1 4-7 8-14 12-16 13-9 6-4 3-4-1-9-9-13-18-9-13v-5l12-13 9-8 17-13 10-6z" fill="#FEFEFE"/>
<path transform="translate(1307,1404)" d="m0 0 9 3 9 6 14 11 10 8 11 9 4 5-2 9-13 18-9 12-6 9-5-2-3-3-8-4-10-8-17-14-8-6-7-7 2-4 8-13 14-19 6-9z" fill="#FEFEFE"/>
<path transform="translate(1308,1186)" d="m0 0 6 1 10 6 11 9 18 14 10 11v5l-9 10-6 7-9 11-9 10-4 2-13-7-10-7-17-13-9-6-4-4 1-4 8-12 16-20 6-9z" fill="#FEFEFE"/>
<path transform="translate(1240,778)" d="m0 0 9 3 12 12 15 20 4 6v4l-10 9-8 7-13 11-16 12-6 1-8-6-10-11-9-11-11-12-1-3 7-5h2l2-4 7-7 10-8 17-13z" fill="#FEFEFE"/>
<path transform="translate(1661,546)" d="m0 0 5 1 8 6 8 8 8 10 10 14 1 6-11 10-13 10-18 14-10 6-5-1-8-9-14-19-9-12-2-4 7-7 5-6 24-18z" fill="#FEFEFE"/>
<path transform="translate(633,858)" d="m0 0 6 1 12 7 14 11 14 10 10 10-1 4-4 8-9 12-9 11-8 10-2 2-4-1-11-6-9-7-14-11-12-11-6-5 1-5 7-9 10-13 8-9 5-8z" fill="#FEFEFE"/>
<path transform="translate(867,714)" d="m0 0 5 1 13 9 10 8 16 12 8 7 3 4-2 9-10 12-7 8-11 13-4 4-7-1-13-10-13-11-16-13-4-5v-6l8-10 7-9 14-19z" fill="#FEFEFE"/>
<path transform="translate(721,596)" d="m0 0 6 2 11 7 12 9 16 13 10 10-1 6-7 9-6 7-8 10-11 13-10-3-11-8-25-20-8-7-1-5 5-10 7-9 10-11 8-11z" fill="#FEFEFE"/>
<path transform="translate(1490,798)" d="m0 0h6l7 6 12 18 11 15 1 4-11 11-14 11-9 8-9 7-8 6-5 1-8-9-12-17-10-14-2-4 1-5 9-8 11-9 13-10 13-9z" fill="#FEFEFE"/>
<path transform="translate(887,1066)" d="m0 0 9 5 8 9 8 10 14 18 1 4-7 8-11 9-10 8h-2l-2 4-10 8-8 4-6-3-7-7-9-11-13-16-5-9 10-8 12-11 11-10 14-10z" fill="#FEFEFE"/>
<path transform="translate(1184,714)" d="m0 0 9 5 8 9 12 16 6 9 3 5-2 4-7 7-14 11-10 9-16 12-6 1-12-12-14-19-6-8v-6l7-8 11-9 15-14z" fill="#FEFEFE"/>
<path transform="translate(1551,416)" d="m0 0 6 1 9 7 13 17 7 11 1 8-8 10-8 7-14 11-13 10-9 5-7-6-6-7-12-16-7-9-1-4 4-8 9-9 11-9 10-9z" fill="#FEFEFE"/>
<path transform="translate(588,1202)" d="m0 0 4 1 9 8 10 13 7 9 8 11 1 3-7 8-14 12-8 6-10 9-12 9-4-1-6-5-13-17-9-12-5-8 1-5 13-11 9-9 11-9 12-10z" fill="#FEFEFE"/>
<path transform="translate(1563,737)" d="m0 0 7 1 8 7 14 20 5 10 1 7-7 8-11 9-16 13-9 7-8 5-4-1-7-8-8-10-11-18-3-6 1-5 17-17 11-8 13-10z" fill="#FEFEFE"/>
<path transform="translate(1444,1187)" d="m0 0 9 3 11 8 13 11 8 6 11 9 5 6-2 5-10 10-8 10-13 14-5 3-9-3-12-8-15-13-10-8-8-8 2-4 4-4 6-9 8-8 8-11 4-6z" fill="#FEFEFE"/>
<path transform="translate(1170,946)" d="m0 0h6l8 6 7 7 10 13 9 13 3 3-2 4-8 8-13 10-8 7-13 11-9 5-8-8-7-8-13-17-9-11 1-4 11-9 4-4h2l2-4 12-11 12-9z" fill="#FEFEFE"/>
<path transform="translate(513,1264)" d="m0 0h6l9 7 10 12 11 16 3 5v5l-8 9-13 10-10 9-8 7-5 4-4 2-5-1-9-9-12-16-10-14-1-2v-6l8-8 11-9 8-7 14-11z" fill="#FEFEFE"/>
<path transform="translate(1337,1320)" d="m0 0 9 3 15 10 12 10 9 7 9 10 1 3-7 13-8 10-4 6-10 13-2 2-5-1-11-6-26-20-9-7-4-4 1-5 8-15 11-14 7-11z" fill="#FEFEFE"/>
<path transform="translate(770,749)" d="m0 0 8 1 16 10 14 12 10 7 7 9-1 5-6 10-16 20-7 9-2 2-5-1-12-6-15-12-13-10-8-7-3-5 6-8 4-7 10-11 7-10z" fill="#FEFEFE"/>
<path transform="translate(441,1323)" d="m0 0h6l6 4 8 8 15 24 2 6-1 6-9 8-7 5-4 5-9 7-10 8-8 4-5-2-10-9-9-11-12-18 1-6 7-9h2v-2l11-9 16-12z" fill="#FEFEFE"/>
<path transform="translate(659,1144)" d="m0 0h6l6 4 9 10 14 21 2 7-1 6-6 7-9 7-3 3h-2v2l-10 7-8 7-8 5-4-1-9-7-6-7-13-18-5-8 2-5 11-12 13-12 11-9z" fill="#FEFEFE"/>
<path transform="translate(1166,838)" d="m0 0h6l8 6 13 14 12 16 3 5-2 4-6 7-8 7-12 10-10 8-13 9-4-1-7-7-8-10-13-19-5-8 1-4 11-9 11-10 9-7z" fill="#FEFEFE"/>
<path transform="translate(646,536)" d="m0 0 6 1 13 9 10 8 11 8 11 9 3 4 1 4-5 10-11 14-7 9-8 10-3 2-10-6-16-13-14-11-11-10-2-3 1-5 14-18 9-12z" fill="#FEFEFE"/>
<path transform="translate(688,1451)" d="m0 0 6 2 10 11 11 14 8 13 1 6-9 9-16 12-10 8-16 12-4-1-6-5-7-9-14-19-5-9 2-4 5-6 10-8 10-9 9-7 12-9z" fill="#FEFEFE"/>
<path transform="translate(573,477)" d="m0 0 6 1 10 6 11 9 16 13 11 10v8l-6 9-10 12-9 11-6 7-5-2-12-6-11-9-8-7-12-9-7-8 2-5 6-12 8-8 10-13z" fill="#FEFEFE"/>
<path transform="translate(794,655)" d="m0 0 6 1 9 6 13 11 14 11 10 8 2 3-1 9-6 8-11 13-9 11-7 5-17-9-14-11-13-10-5-4-2-4 1-7 6-10 10-13z" fill="#FEFEFE"/>
<path transform="translate(1100 1e3)" d="m0 0 6 1 9 7 9 10 10 14 6 9 3 2-11 12-11 8-11 10-8 6-6 5-6 2-8-7-9-11-13-17-6-8 1-5 9-9 8-7 10-9 9-7z" fill="#FEFEFE"/>
<path transform="translate(1382,1244)" d="m0 0 6 1 11 8 13 11 10 8 11 11 1 6-10 11-11 14-10 13-3 4-5-2-15-9-8-6-11-9-10-8-3-7 6-12 14-18 11-13z" fill="#FEFEFE"/>
<path transform="translate(700,690)" d="m0 0 6 1 17 12 16 13 11 7 3 5v6l-8 14-9 11-6 8-8 10-6-1-11-7-12-10-16-12-8-7 1-7 4-8 10-14 8-9z" fill="#FEFEFE"/>
<path transform="translate(1417,858)" d="m0 0 4 1 10 9 16 24 5 9-4 6-10 9-9 7-13 10-8 7-8 5h-3l-4-6-7-7-12-17-9-14 3-5 8-9 19-14 13-10z" fill="#FEFEFE"/>
<path transform="translate(1522,1358)" d="m0 0 7 2 14 10 15 11 8 6 7 6 2 6-7 11-7 9-7 8-7 11-7 7-6-2-10-8-11-9-14-11-10-9 1-6 6-10 8-11 9-12 7-8z" fill="#FEFEFE"/>
<path transform="translate(631,633)" d="m0 0 5 1 13 9 10 8 11 8 10 8 4 6-2 5-6 11-9 10-8 12-7 7-1 2-4-1-11-7-11-9-13-10-10-8-3-3-1-6 6-10 7-9 11-14 7-8z" fill="#FEFEFE"/>
<path transform="translate(593,714)" d="m0 0 6 1 10 6 22 18 13 10 5 7-4 7-8 10-5 5-6 7-7 11-5 5-10-4-13-11-8-6-16-13-5-5 1-7 12-17 9-12 7-10z" fill="#FEFEFE"/>
<path transform="translate(1257,655)" d="m0 0 5 1 7 6 18 24 7 11 1 5-15 13-14 11-11 9-10 6-5-1-7-5-13-17-7-10-5-8 1-4 12-11 8-7 10-9 12-9z" fill="#FEFEFE"/>
<path transform="translate(606,1407)" d="m0 0 9 2 9 9 10 13 8 10 3 5-1 6-4 6-9 7-11 9-14 11-8 4-4 3-8-7-7-7-10-14-10-15 2-5 15-15 12-9 10-8z" fill="#FEFEFE"/>
<path transform="translate(1481,1434)" d="m0 0 5 1 13 9 10 9 11 9 10 9 3 5-1 6-9 12-10 12-7 11-4 4h-6l-14-10-11-9-12-10-8-7-4-5 1-4 8-9 10-14 10-13z" fill="#FEFEFE"/>
<path transform="translate(733,830)" d="m0 0 8 1 14 9 18 14 9 6 6 8-1 5-6 10-9 12-10 11-5 8-4 1-13-7-10-9-14-10-8-6-6-6 2-6 8-14 9-11z" fill="#FEFEFE"/>
<path transform="translate(370,1380)" d="m0 0 4 1 11 11 7 10 8 10 8 11-1 4-17 16-10 7-7 7-15 9-5-1-8-7-8-9-9-14-4-9v-6l11-12 12-11 19-14z" fill="#FEFEFE"/>
<path transform="translate(677,1351)" d="m0 0 6 1 6 4 9 9 7 9 9 12 3 3-1 5-6 8-15 13-13 10-9 6-2 1h-7l-8-7-7-7-18-22-2-5 15-16 9-7 13-11 8-5z" fill="#FEFEFE"/>
<path transform="translate(1029,1064)" d="m0 0h6l6 4 10 9 10 13 7 11 3 3-2 6-7 7-14 11-11 9-9 7-7 2-6-3-12-13-11-14-4-5v-2l-4-2 1-5 4-6 4-5 13-10 10-9 10-7z" fill="#FEFEFE"/>
<path transform="translate(744,1186)" d="m0 0 5 1 8 6 8 8 9 11 7 10 2 3-1 5-7 9-13 10-8 7-8 6-7 5-9 2-9-8-11-14-13-16-1-3 9-11 9-9 22-18z" fill="#FEFEFE"/>
<path transform="translate(957,1009)" d="m0 0 6 2 10 9 11 16 8 11 4 7-2 4-17 16-11 8-9 8-8 4-6-2-10-7-8-10-14-21 1-4 7-9 15-14 8-7z" fill="#FEFEFE"/>
<path transform="translate(1241,888)" d="m0 0 7 1 10 8 13 17 9 13 1 6-10 10-11 9-10 9-9 7-6 3h-5l-11-8-7-8-8-10-11-13v-3l9-7 8-8 8-7 13-11z" fill="#FEFEFE"/>
<path transform="translate(1476,478)" d="m0 0 7 1 7 6 10 14 10 15 3 5-2 5-7 7-14 11-17 14-10 6-4-1-8-6-9-11-14-19-3-5v-2l10-8 13-11 12-10z" fill="#FEFEFE"/>
<path transform="translate(1342,918)" d="m0 0 5 1 8 7 12 16 10 14 2 3-1 5-11 9-13 11-10 8-14 11-6 2-8-9-13-17-8-13-2-7 5-6 11-9 8-7 11-9z" fill="#FEFEFE"/>
<path transform="translate(675,1243)" d="m0 0 5 1 9 9 8 11 10 13 4 10-2 5-12 11-13 10-12 10-6 3-3 2-5-1-14-14-10-14-6-10-1-6 5-5 12-13 19-14 10-7z" fill="#FEFEFE"/>
<path transform="translate(1452,1301)" d="m0 0 6 1 17 12 9 8 8 7 10 9 1 7-8 11-8 10-7 10-6 7h-2l-2 4-2 1-8-6-19-14-18-14-3-4 1-9 8-13 10-13 10-12z" fill="#FEFEFE"/>
<path transform="translate(958,1120)" d="m0 0h7l6 3 10 12 9 13 7 14v6l-12 12-12 9-13 10-9 3-5-1-10-8-7-8-10-15-5-7 1-4 9-11 10-9 13-10z" fill="#FEFEFE"/>
<path transform="translate(603,1302)" d="m0 0 7 1 6 5 8 11 11 14 6 8v5l-4 5-8 7-9 8-9 6-5 5-11 8-6 1-7-6-9-11-9-12-7-13 1-6 10-10 11-9 14-11z" fill="#FEFEFE"/>
<path transform="translate(559,577)" d="m0 0h6l10 6 14 12 9 6 14 12 1 6-6 9-10 13-4 5h-2l-2 4-9 12-4-1-10-6-12-9-22-18-3-6 3-9 4-8 8-10 10-13z" fill="#FEFEFE"/>
<path transform="translate(1402,537)" d="m0 0 5 1 9 7 8 10 11 15 5 9-1 4-8 8-13 10-14 11-11 8-4 2-5-1-8-9-10-14-11-15-1-6 14-12 13-12 10-8z" fill="#FEFEFE"/>
<path transform="translate(821,1236)" d="m0 0h5l10 9 14 18 7 10 2 4-1 5-9 9-13 10-20 15-6 4h-3v-2l-5-2-7-8-12-16-7-10-2-4 1-5 8-8 8-7 10-9 18-12z" fill="#FEFEFE"/>
<path transform="translate(1025,954)" d="m0 0 7 1 8 5 9 10 10 14 5 10-1 7-7 7-16 14-12 8-10 7-5-2-10-7-9-13-10-14-2-5 3-9 13-13 12-9 11-9z" fill="#FEFEFE"/>
<path transform="translate(746,1295)" d="m0 0 9 1 8 6 10 12 13 17 3 2-1 5-7 7-10 8-9 7-11 9-7 6-2 1h-6l-6-4-11-12-15-20-2-3 2-9 13-11 8-7 10-8z" fill="#FEFEFE"/>
<path transform="translate(534,1360)" d="m0 0 6 1 6 5 18 24 7 9-1 4-6 7-11 9-10 8-13 10-8 6-5-1-8-7-13-18-11-17-1-3 4-5 11-9 15-12 13-8z" fill="#FEFEFE"/>
<path transform="translate(1525,658)" d="m0 0 6 1 8 6 10 13 7 9 7 13-1 5-9 8-13 10-11 9-10 6-4 2h-5l-11-11-9-12-10-12-4-5v-4l10-8 13-11 13-10 11-8z" fill="#FEFEFE"/>
<path transform="translate(1097,896)" d="m0 0 5 1 9 7 9 11 8 10 4 6 1 6-1 7-5 6-8 7-3 3h-2v2l-13 10-10 6-5 2-8-7-8-8-9-11-9-13-1-6 3-5 12-11 13-10 9-8z" fill="#FEFEFE"/>
<path transform="translate(1267,1264)" d="m0 0 5 1 13 8 26 20 5 5 5 6-6 11-13 16-11 15-3 4-6-2-6-4-13-11-16-12-10-9-1-2v-6l4-6 8-11 8-9 9-13z" fill="#FEFEFE"/>
<path transform="translate(1455,604)" d="m0 0 7 1 9 8 10 14 6 8 6 12-3 5-3 1-1 3-11 9-8 7-9 7-14 8-3 1-12-12-21-28-2-4 4-4 7-5 5-6 14-11 13-10z" fill="#FEFEFE"/>
<path transform="translate(1311,721)" d="m0 0 7 1 6 4 7 7 9 12 8 11 3 7-4 6-10 9-11 9-17 13-5 4-4-1-10-6-16-21-8-11 1-5 4-6 7-7 8-7 12-9 11-9z" fill="#FEFEFE"/>
<path transform="translate(523,657)" d="m0 0 6 1 13 9 13 11 10 8 9 7 2 3v6l-7 11-11 12-10 14-3 3-7-1-14-9-10-8-14-11-5-4-3-5 2-6 14-20 10-14z" fill="#FEFEFE"/>
<path transform="translate(1328,599)" d="m0 0h7l6 4 9 10 10 14 5 10-1 7-7 7-10 8-11 9-13 10-6 4-5-2-8-6-8-11-8-12-6-8 1-5 6-9 14-12 10-8 13-9z" fill="#FEFEFE"/>
<path transform="translate(1410,1377)" d="m0 0 6 2 11 7 10 8 14 12 8 7 3 4-3 9-6 9-10 13-9 12-5 4-14-8-18-14-14-11-4-6v-5l6-9 12-16 7-10z" fill="#FEFEFE"/>
<path transform="translate(1379,776)" d="m0 0h10l6 4 10 10 9 12 6 12 1 5-6 7-11 9-12 9h-2v2l-13 10-3 2h-4l-4-5-5-5-10-12-10-13-3-3v-8l7-8 10-10 14-11 8-6z" fill="#FEFEFE"/>
<path transform="translate(1312,832)" d="m0 0 6 1 8 5 8 8 8 11 7 11 2 4-1 5-9 9-14 11-13 11-9 6h-4l-3-3-6-4-7-8-12-16-6-9 1-4 4-7 7-7 11-9 13-10z" fill="#FEFEFE"/>
<path transform="translate(1455,715)" d="m0 0 6 2 10 10 6 8 8 10 7 13-1 4-12 11-9 7-14 12-11 7-5 1-10-11-14-19-10-13 2-4 14-13 14-11 11-9z" fill="#FEFEFE"/>
<path transform="translate(892,1177)" d="m0 0 6 2 6 5 10 14 11 15 3 7v5l-8 8-24 18-10 7-6 4-4-2-14-14-13-18-4-7 1-6 13-12 8-8 10-8 12-9z" fill="#FEFEFE"/>
<path transform="translate(664,774)" d="m0 0 7 1 12 7 13 10 11 8 7 5 4 7-4 8-11 14-9 11-8 11-5 1-10-6-13-11-13-10-11-9-2-2 1-6 12-18 5-5 12-15z" fill="#FEFEFE"/>
<path transform="translate(1384,662)" d="m0 0 5 1 7 5 9 12 11 14 4 8-1 6-7 8-10 9-13 10-8 6-6 4-5 1-13-13-14-19-6-9-1-5 12-11 14-11 12-9z" fill="#FEFEFE"/>
<path transform="translate(1590,604)" d="m0 0 6 1 7 7 10 13 9 14 5 10-3 5-8 7-13 10-10 9-9 3-9-6-8-9-13-18-6-8 2-6 7-8 13-11 18-12z" fill="#FEFEFE"/>
<path transform="translate(1210,1217)" d="m0 0 6 1 6 4 11 9 12 9 6 6-2 4-4 6-6 7-6 8-7 8-9 12-9-2-11-8-13-11-9-7-5-5 1-5 7-8 11-9 10-10 8-7z" fill="#FEFEFE"/>
<path transform="translate(842,804)" d="m0 0 6 2 12 7 11 10 11 9 4 6-1 5-7 7-10 8-11 9-8 7-7 4-4-2-11-8-14-10-5-5 7-11 8-11 7-9z" fill="#FEFEFE"/>
<path transform="translate(706,914)" d="m0 0 6 2 11 7 11 10 10 8 6 7v5l-6 7-9 7h-2v2l-11 9-8 8-6 4-4-1-9-9-13-10-6-5-2-5 7-9 4-6 10-12 10-17z" fill="#FEFEFE"/>
<path transform="translate(1281,1162)" d="m0 0 5 1 2 3v6l-7 11-11 13-10 13-4 4-8-1-12-8v-3l7-9 12-11 8-7 13-10z" fill="#FEFEFE"/>
<path transform="translate(806,887)" d="m0 0 9 2 4 2 1 4-6 8-14 12-10 10-11 7-3-1 1-8 6-9 9-10 10-13z" fill="#FEFEFE"/>
</svg>

            <h1 style="margin: 0; font-size: 24px;">AI Tax Automation Livestream</h1>
        </div>
        
        <div style="padding: 30px;">
            <p>Hi {name},</p>
            
            <p><strong>Thanks for signing up for the stream!</strong></p>
            
            <div>
                <a href="https://youtube.com/live/4vAqaKfexeE" style="display: inline-block; text-decoration: none; border: 2px solid #000;">
    <img src="https://img.youtube.com/vi/4vAqaKfexeE/hqdefault.jpg" 
         alt="AI Tax Automation Livestream" 
         style="width: 300px; max-width: 100%; height: auto; display: block;">
                </a>
                <p style="margin-top: 10px;"><a href="https://youtube.com/live/4vAqaKfexeE" style="color: #000; text-decoration: none; font-weight: bold;">Click to visit</a></p>
            </div>
            
            <p>We're going to email you again just before the stream starts as a quick reminder.</p>
            
            <div style="background-color: #f8f8f8; border-left: 4px solid #000; padding: 20px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Registration ID:</strong> {registration_id}</p>
                <p style="margin: 5px 0;"><strong>Format:</strong> Online Livestream</p>
                <p style="margin: 5px 0;"><strong>Cost:</strong> FREE</p>
            </div>
            
            <h3 style="margin-top: 30px;">Why A.I. Automation Right Now?</h3>
            <p>AI makes software easier and easier to create. Instead of getting software experts to learn problems and then solve them, it's making more and more sense to have the experts who understand the problem intimately already learn how to build software using tools like Claude, MCP and n8n. See for instance the <a href="https://www.reddit.com/r/PowerApps/comments/1ce5kd9/are_there_really_tons_of_citizen_developers_out/"> rise of Citizen Developers</a></p>

            <p>A great example is the story of <a href="https://www.linkedin.com/pulse/how-i-automated-friends-invoicing-process-one-weekend-rich-nasser/">Rich Nasser</a> who automated a 3-day invoice processing process into a 45-minute task using Power Automate. Rich understood the invoicing problem intimately—he knew which exceptions broke the system, which edge cases mattered, and what actually needed to be solved. With AI tools, he could solve it himself rather than trying to explain it to a developer.</p>

            <p>I'm always keen to chat about this topic, so if you have any questions, feel free to reply to this email or add me on <a href="https://www.linkedin.com/in/louka-ewington-pitsos-2a92b21a0/">LinkedIn</a>.</p>

            <h3>What We'll cover in the livestream:</h3>
            <ul>
                <li>How to automate tax form processing with AI</li>
                <li>Building intelligent document extraction workflows</li>
                <li>Integrating AI with existing accounting systems</li>
                <li>Real-world case studies and demonstrations</li>
            </ul>
            
            <p style="margin-top: 30px;">If you have any questions, feel free to reach out to us.</p>
            
            <p>See you soon!,<br>
            - Louka</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 14px;">
            <p>© 2024 AI Automation Mastery. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    email_body_text = f"""
Hi {name},

Thanks for signing up for the stream

Watch the livestream here: https://youtube.com/live/4vAqaKfexeE

We're going to email you again just before the stream starts as a quick reminder.

Registration Details:
- Registration ID: {registration_id}
- Format: Online Livestream
- Cost: FREE

Why A.I. Automation Right Now?
AI makes software easier and easier to create. Instead of getting software experts to learn problems and then solve them, it's making more and more sense to have the experts who understand the problem intimately already learn how to build software using tools like Claude, MCP and n8n. See for instance the rise of Citizen Developers: https://www.reddit.com/r/PowerApps/comments/1ce5kd9/are_there_really_tons_of_citizen_developers_out/

A great example is the story of Rich Nasser (https://www.linkedin.com/pulse/how-i-automated-friends-invoicing-process-one-weekend-rich-nasser/) who automated a 3-day invoice processing process into a 45-minute task using Power Automate. Rich understood the invoicing problem intimately—he knew which exceptions broke the system, which edge cases mattered, and what actually needed to be solved. With AI tools, he could solve it himself rather than trying to explain it to a developer.

I'm always keen to chat about this topic, so if you have any questions, feel free to reply to this email or add me on LinkedIn: https://www.linkedin.com/in/louka-ewington-pitsos-2a92b21a0/

What We'll cover in the livestream:
• How to automate tax form processing with AI
• Building intelligent document extraction workflows
• Integrating AI with existing accounting systems
• Real-world case studies and demonstrations

If you have any questions, feel free to reach out to us.

See you soon!,
- Louka
    """
    
    # Send email via SES
    return {
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': email_body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': email_body_html,
                    'Charset': 'UTF-8'
                }
            }
        }
    
def send_user_confirmation_email(name, email, registration_id):
    """
    Send confirmation email to user for livestream registration
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    
    if not contact_form_email:
        logger.error("Missing CONTACT_FORM_EMAIL environment variable")
        raise ValueError("Email configuration error")
    
    email_message = create_email_message(name, registration_id)
    
    # Send email via SES
    response = ses_client.send_email(
        Source=contact_form_email,
        Destination={'ToAddresses': [email]},
        Message=email_message
    )
    
    return response['MessageId']


def send_application_confirmation_email(name, email, registration_id):
    """
    Send confirmation email to user for application submission
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    
    if not contact_form_email:
        logger.error("Missing CONTACT_FORM_EMAIL environment variable")
        raise ValueError("Email configuration error")
    
    subject, html_body, text_body = get_application_confirmation_email(name, registration_id)
    
    # Send email via SES
    response = ses_client.send_email(
        Source=contact_form_email,
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'UTF-8'
            },
            'Body': {
                'Text': {
                    'Data': text_body,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': html_body,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    
    return response['MessageId']


def send_admin_notification(name, email, registration_id, registration_type='livestream', application_data=None):
    """
    Send notification to admin about new registration
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    admin_email = os.environ.get('ADMIN_EMAIL')
    
    if not contact_form_email or not admin_email:
        logger.error("Missing required email environment variables")
        raise ValueError("Email configuration error")
    
    if registration_type == 'application':
        subject = f"[Application] New application from {name}"
        course_info = "AI Automation for Non Coders (01_ai_automation_for_non_coders)"
        status_info = "Applied (Awaiting Review)"
        
        # Build detailed application email body
        email_body = f"""
New Application Submitted

Basic Information:
- Name: {name}
- Email: {email}
- Phone: {application_data.get('phone', 'Not provided')}
- Company: {application_data.get('company', 'Not provided')}
- Job Title: {application_data.get('jobTitle', 'Not provided')}

Technical Background:
- Coding Experience: {application_data.get('experience', 'Not provided')}

Course Commitment:
- Time Commitment (hrs/day): {application_data.get('timeCommitment', 'Not provided')}
- Attendance Confirmed: {'Yes' if application_data.get('attendance') else 'No'}
- Consent Given: {'Yes' if application_data.get('consent') else 'No'}

Application Details:
- Automation Interest: {application_data.get('automationInterest', 'Not provided')}

- Current Barriers: {application_data.get('automationBarriers', 'Not provided')}

Course Information:
- Registration ID: {registration_id}
- Course: {course_info}
- Status: {status_info}
- Registration Time: {datetime.utcnow().isoformat()}

This is an automated notification for a new application.
        """
    else:
        subject = f"[Livestream Registration] New signup from {name}"
        course_info = "AI Tax Automation Livestream (tax-livestream-01)"
        status_info = "Paid (Free Registration)"
        
        email_body = f"""
New {registration_type.title()}

Registration Details:
- Name: {name}
- Email: {email}
- Registration ID: {registration_id}
- Course: {course_info}
- Status: {status_info}
- Registration Time: {datetime.utcnow().isoformat()}

This is an automated notification for a new {registration_type}.
        """
    
    # Send email via SES
    response = ses_client.send_email(
        Source=contact_form_email,
        Destination={'ToAddresses': [admin_email]},
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
        }
    )
    
    return response['MessageId']