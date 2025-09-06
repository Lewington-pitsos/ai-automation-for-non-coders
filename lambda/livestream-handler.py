import json
import boto3
import uuid
from datetime import datetime
import logging
import os
from meta_conversions_api import handle_complete_registration

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
        
        # Fixed course ID for livestream
        course_id = 'tax-livestream-01'
        
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
                # Still return success to avoid revealing duplicate registrations
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'message': 'Registration successful',
                        'registration_id': existing_item["Item"].get("registration_id")
                    })
                }
        except Exception as e:
            logger.error(f"Error checking existing registration: {str(e)}")
        
        # Create new registration
        registration_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create registration item with automatic paid status
        item = {
            "course_id": course_id,
            "email": email,
            "registration_id": registration_id,
            "name": name,
            "payment_status": "paid",  # Automatically mark as paid
            "payment_amount": 0,  # $0 for free livestream
            "registration_date": timestamp,
            "registration_type": "livestream",
            "stripe_session_id": "",  # No Stripe session for free registration
        }
        
        # Store in DynamoDB
        table.put_item(Item=item)
        logger.info(f"Livestream registration created: {registration_id} for email: {email}")
        
        # Send confirmation email to user
        try:
            send_user_confirmation_email(name, email, registration_id)
            logger.info(f"Confirmation email sent to {email}")
        except Exception as email_error:
            logger.error(f"Error sending user confirmation email: {str(email_error)}")
            # Don't fail the registration if email fails
        
        # Send notification to admin
        try:
            send_admin_notification(name, email, registration_id)
            logger.info(f"Admin notification sent for registration: {registration_id}")
        except Exception as admin_error:
            logger.error(f"Error sending admin notification: {str(admin_error)}")
            # Don't fail the registration if admin notification fails
        
        # Send CompleteRegistration event to Meta Conversions API
        try:
            user_agent = event.get("headers", {}).get("User-Agent", "")
            user_data = {
                "email": email,
                "client_user_agent": user_agent
            }
            
            # Get the source URL from the event if available
            event_source_url = event.get("headers", {}).get("referer") or event.get("headers", {}).get("Referer")
            
            meta_result = handle_complete_registration(user_data, event_source_url, registration_id)
            if meta_result["success"]:
                logger.info(f"Meta Conversions API CompleteRegistration event sent for: {registration_id}")
            else:
                logger.warning(f"Failed to send Meta Conversions API event: {meta_result.get('error')}")
        except Exception as meta_error:
            logger.error(f"Error sending Meta Conversions API event: {str(meta_error)}")
            # Don't fail the registration if Meta API fails
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Registration successful',
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


def send_user_confirmation_email(name, email, registration_id):
    """
    Send confirmation email to user for livestream registration
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    
    if not contact_form_email:
        logger.error("Missing CONTACT_FORM_EMAIL environment variable")
        raise ValueError("Email configuration error")
    
    subject = "Welcome to the AI Tax Automation Livestream!"
    
    email_body_html = f"""
    <html>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #000; color: #fff; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">AI Tax Automation Livestream</h1>
        </div>
        
        <div style="padding: 30px;">
            <p>Hi {name},</p>
            
            <p>Thank you for registering for our <strong>AI Tax Automation Livestream</strong>!</p>
            
            <p>We're excited to have you join us for this free online session where we'll demonstrate how AI can revolutionize tax preparation and accounting workflows.</p>
            
            <div style="background-color: #f8f8f8; border-left: 4px solid #000; padding: 20px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Registration ID:</strong> {registration_id}</p>
                <p style="margin: 5px 0;"><strong>Format:</strong> Online Livestream</p>
                <p style="margin: 5px 0;"><strong>Cost:</strong> FREE</p>
            </div>
            
            <h3 style="margin-top: 30px;">What's Next?</h3>
            <p>We'll send you the livestream link and access details closer to the event date. Make sure to check your email regularly.</p>
            
            <h3>What You'll Learn:</h3>
            <ul>
                <li>How to automate tax form processing with AI</li>
                <li>Building intelligent document extraction workflows</li>
                <li>Integrating AI with existing accounting systems</li>
                <li>Real-world case studies and demonstrations</li>
            </ul>
            
            <p style="margin-top: 30px;">If you have any questions, feel free to reach out to us.</p>
            
            <p>Best regards,<br>
            The AI Automation Team</p>
        </div>
        
        <div style="background-color: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 14px;">
            <p>© 2024 AI Automation Mastery. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    email_body_text = f"""
Hi {name},

Thank you for registering for our AI Tax Automation Livestream!

We're excited to have you join us for this free online session where we'll demonstrate how AI can revolutionize tax preparation and accounting workflows.

Registration Details:
- Registration ID: {registration_id}
- Format: Online Livestream
- Cost: FREE

What's Next?
We'll send you the livestream link and access details closer to the event date. Make sure to check your email regularly.

What You'll Learn:
• How to automate tax form processing with AI
• Building intelligent document extraction workflows
• Integrating AI with existing accounting systems
• Real-world case studies and demonstrations

If you have any questions, feel free to reach out to us.

Best regards,
The AI Automation Team
    """
    
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
                    'Data': email_body_text,
                    'Charset': 'UTF-8'
                },
                'Html': {
                    'Data': email_body_html,
                    'Charset': 'UTF-8'
                }
            }
        }
    )
    
    return response['MessageId']


def send_admin_notification(name, email, registration_id):
    """
    Send notification to admin about new livestream registration
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    admin_email = os.environ.get('ADMIN_EMAIL')
    
    if not contact_form_email or not admin_email:
        logger.error("Missing required email environment variables")
        raise ValueError("Email configuration error")
    
    subject = f"[Livestream Registration] New signup from {name}"
    
    email_body = f"""
New Livestream Registration

Registration Details:
- Name: {name}
- Email: {email}
- Registration ID: {registration_id}
- Course: AI Tax Automation Livestream (tax-livestream-01)
- Payment Status: Paid (Free Registration)
- Registration Time: {datetime.utcnow().isoformat()}

This is an automated notification for a new livestream registration.
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