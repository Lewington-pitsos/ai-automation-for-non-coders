import json
import boto3
import uuid
from datetime import datetime
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "course_registrations")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        
        email = body["email"].lower()  # Store email in lowercase for consistent matching
        course_id = body.get("course_id")
        
        # Validate course_id - only accept specific values
        valid_course_ids = ["01_ai_automation_for_non_coders", "test-course"]
        if not course_id or course_id not in valid_course_ids:
            logger.error(f"Invalid course_id: {course_id}")
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "error": "invalid_course_id",
                    "message": "Invalid course ID provided"
                })
            }
        
        # Check if registration already exists for this email and course
        try:
            existing_item = table.get_item(
                Key={
                    "course_id": course_id,
                    "email": email
                }
            )
            
            if "Item" in existing_item:
                logger.info(f"Duplicate registration attempt for email: {email}, course: {course_id}")
                return {
                    "statusCode": 400,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "POST, OPTIONS"
                    },
                    "body": json.dumps({
                        "error": "email_already_registered",
                        "message": "This email has already been registered for this course"
                    })
                }
        except Exception as e:
            logger.error(f"Error checking existing registration: {str(e)}")
        
        registration_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            "course_id": course_id,
            "email": email,
            "registration_id": registration_id,
            "name": body["name"],
            "phone": body.get("phone", ""),
            "company": body.get("company", ""),
            "job_title": body.get("job_title", ""),
            "experience": body.get("experience", ""),
            "referral_source": body.get("referral_source", ""),
            "automation_interest": body.get("automation_interest", ""),
            "dietary_requirements": body.get("dietary_requirements", ""),
            "payment_status": "pending",
            "registration_date": timestamp,
            "stripe_session_id": "",  # Will be populated by webhook
        }
        
        table.put_item(Item=item)
        
        logger.info(f"Registration created: {registration_id} for email: {email}, course: {course_id}")
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "message": "Registration successful",
                "registration_id": registration_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error creating registration: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "error": "Internal server error"
            })
        }