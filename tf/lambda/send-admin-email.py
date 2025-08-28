import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client('ses')

FROM_EMAIL = '${from_email}'
ADMIN_EMAIL = '${admin_email}'

def lambda_handler(event, context):
    try:
        registration_data = event['detail']
        email = registration_data['email']
        name = registration_data['name']
        registration_id = registration_data['registration_id']
        
        subject = f"New Course Registration: {name}"
        
        body_html = f"""
        <html>
        <body>
            <h2>New Course Registration</h2>
            <p>A new student has successfully registered and paid for the course.</p>
            
            <h3>Registration Details:</h3>
            <ul>
                <li><strong>Name:</strong> {name}</li>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Registration ID:</strong> {registration_id}</li>
                <li><strong>Payment Status:</strong> Paid</li>
            </ul>
            
            <p>The welcome email has been sent to the student.</p>
            
            <p>Best regards,<br>Course Registration System</p>
        </body>
        </html>
        """
        
        body_text = f"""
        New Course Registration
        
        A new student has successfully registered and paid for the course.
        
        Registration Details:
        - Name: {name}
        - Email: {email}
        - Registration ID: {registration_id}
        - Payment Status: Paid
        
        The welcome email has been sent to the student.
        
        Best regards,
        Course Registration System
        """
        
        response = ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [ADMIN_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        
        logger.info(f"Admin notification sent for registration {registration_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Admin email sent successfully',
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        logger.error(f"Error sending admin email: {str(e)}")
        raise e