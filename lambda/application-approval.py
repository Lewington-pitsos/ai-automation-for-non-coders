import json
import boto3
import os
import logging
import urllib.parse
from datetime import datetime
from email_templates import get_application_acceptance_email

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")
ses_client = boto3.client('ses')

# Get environment variables
table_name = os.environ.get("TABLE_NAME", "course_registrations")
table = dynamodb.Table(table_name)
base_url = os.environ.get("BASE_URL", "https://fairdinkumsystems.com")

def lambda_handler(event, context):
    """
    Handle application approval - change status from 'applied' to 'pending' and send acceptance email
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
        application_id = body.get('application_id')
        if not application_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing application_id'})
            }
        
        # Get the application from database
        try:
            # Scan for the application by registration_id since we don't have course_id+email as keys
            response = table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('registration_id').eq(application_id)
            )
            
            if not response['Items']:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({'error': 'Application not found'})
                }
            
            application = response['Items'][0]
            
        except Exception as e:
            logger.error(f"Error retrieving application: {str(e)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Database error'})
            }
        
        # Verify this is actually an application
        if application.get('payment_status') != 'applied':
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Application is not in applied status'})
            }
        
        # Update status to 'pending'
        try:
            table.update_item(
                Key={
                    'course_id': application['course_id'],
                    'email': application['email']
                },
                UpdateExpression="SET payment_status = :status, approval_date = :date",
                ExpressionAttributeValues={
                    ':status': 'pending',
                    ':date': datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Application {application_id} approved and status changed to pending")
            
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Failed to update application status'})
            }
        
        # Create registration URL with pre-filled data
        registration_url = create_registration_url(application)
        
        # Send acceptance email
        try:
            send_acceptance_email(
                application['name'], 
                application['email'], 
                application_id, 
                registration_url
            )
            logger.info(f"Acceptance email sent to {application['email']}")
            
        except Exception as email_error:
            logger.error(f"Error sending acceptance email: {str(email_error)}")
            # Still consider the approval successful even if email fails
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Application approved successfully',
                'application_id': application_id,
                'registration_url': registration_url
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }


def create_registration_url(application):
    """
    Create a registration URL with pre-filled data from the application
    """
    # Extract application data for URL parameters
    params = {
        'applicant_id': application['registration_id'],
        'email': application['email'],
        'firstName': application['name'].split()[0] if application['name'] else '',
        'lastName': ' '.join(application['name'].split()[1:]) if len(application['name'].split()) > 1 else '',
        'phone': application.get('phone', ''),
        'company': application.get('company', ''),
        'jobTitle': application.get('job_title', ''),
        'automationInterest': application.get('automation_interest', '')
    }
    
    # URL encode parameters
    query_string = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    
    return f"{base_url}/register.html?{query_string}"


def send_acceptance_email(name, email, application_id, registration_url):
    """
    Send acceptance email to the applicant
    """
    contact_form_email = os.environ.get('CONTACT_FORM_EMAIL')
    
    if not contact_form_email:
        logger.error("Missing CONTACT_FORM_EMAIL environment variable")
        raise ValueError("Email configuration error")
    
    subject, html_body, text_body = get_application_acceptance_email(name, application_id, registration_url)
    
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