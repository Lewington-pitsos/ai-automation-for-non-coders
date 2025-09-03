import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ses_client = boto3.client('ses')
s3_client = boto3.client('s3')

FROM_EMAIL = '${from_email}'
BUCKET_NAME = '${bucket_name}'

def lambda_handler(event, context):
    try:
        registration_data = event['detail']
        email = registration_data['email']
        name = registration_data['name']
        
        subject = "Welcome to the Course! 🎉"
        
        body_html = f"""
        <html>
        <body>
            <h2>Welcome {name}!</h2>
            <p>Thank you for registering for our course! Your payment has been successfully processed.</p>
            
            <h3>What happens next?</h3>
            <ul>
                <li>You will receive another email with your login details within 24 hours</li>
                <li>Please arrive 10 minutes early for the in-person sessions on September 27th and October 4th</li>
                <li>Sessions start at 10:00 AM sharp and you will need to be let into the building</li>
                <li>Address: 3/251 Flinders Ln, Melbourne VIC 3000, 2nd Level, Room 2, Sue Healy Room</li>
            </ul>
            
            <h3>What to bring:</h3>
            <ul>
                <li>A laptop</li>
                <li>A charger</li>
                <li>No lunch needed - it will be catered!</li>
            </ul>
            
            <h3>Get started now!</h3>
            <p>While you wait, check out these helpful videos:</p>
            <ul>
                <li><a href="https://www.youtube.com/watch?v=R9OHn5ZF4Uo&ab_channel=CGPGrey">How A.I.s Learn (9 minutes)</a> - A fun high-level overview</li>
                <li><a href="https://www.youtube.com/watch?v=Fy1UCBcgF2o&ab_channel=CharlieChang">How to use N8n</a> - Getting started with automation</li>
            </ul>
            
            <p>We're excited to have you in the course!</p>
            <p>Best regards,<br>The Course Team</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Welcome {name}!
        
        Thank you for registering for our course! Your payment has been successfully processed.
        
        What happens next?
        - You will receive another email with your login details within 24 hours
        - Please arrive 10 minutes early for the in-person sessions on September 27th and October 4th
        - Sessions start at 10:00 AM sharp and you will need to be let into the building
        - Address: 3/251 Flinders Ln, Melbourne VIC 3000, 2nd Level, Room 2, Sue Healy Room
        
        What to bring:
        - A laptop
        - A charger
        - No lunch needed - it will be catered!
        
        Get started now!
        While you wait, check out these helpful videos:
        - How A.I.s Learn: https://www.youtube.com/watch?v=R9OHn5ZF4Uo&ab_channel=CGPGrey
        - How to use N8n: https://www.youtube.com/watch?v=Fy1UCBcgF2o&ab_channel=CharlieChang
        
        We're excited to have you in the course!
        
        Best regards,
        The Course Team
        """
        
        response = ses_client.send_email(
            Source=FROM_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Text': {'Data': body_text},
                    'Html': {'Data': body_html}
                }
            }
        )
        
        logger.info(f"Welcome email sent to {email}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Email sent successfully',
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise e