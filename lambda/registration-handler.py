import json
import boto3
from boto3.dynamodb.conditions import Attr
import uuid
from datetime import datetime
import logging
import os
from meta_conversions_api import handle_complete_registration

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
        applicant_id = body.get("applicant_id")  # For auto-fill from approved applications
        
        
        if not body.get("dietary_requirements"):
            logger.error("Missing required field: dietary_requirements")
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "error": "missing_required_field",
                    "message": "dietary_requirements is required"
                })
            }
        
        # Validate course_id - only accept specific values
        valid_course_ids = ["01_ai_automation_for_non_coders", "test-course", "tax-livestream-01"]
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
        
        # If applicant_id is provided, verify it exists and is in 'pending' status
        if applicant_id:
            try:
                # Scan for the application by registration_id
                response = table.scan(
                    FilterExpression=Attr('registration_id').eq(applicant_id)
                )
                
                if not response['Items']:
                    logger.error(f"Application {applicant_id} not found")
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "Content-Type",
                            "Access-Control-Allow-Methods": "POST, OPTIONS"
                        },
                        "body": json.dumps({
                            "error": "invalid_application",
                            "message": "Application not found or invalid"
                        })
                    }
                
                application = response['Items'][0]
                
                # Verify the application is in 'pending' status
                if application.get('payment_status') != 'pending':
                    logger.error(f"Application {applicant_id} is not in pending status: {application.get('payment_status')}")
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "Content-Type",
                            "Access-Control-Allow-Methods": "POST, OPTIONS"
                        },
                        "body": json.dumps({
                            "error": "invalid_application_status",
                            "message": "Application is not approved for registration"
                        })
                    }
                
                # Verify the email matches
                if application['email'] != email:
                    logger.error(f"Email mismatch for application {applicant_id}: {application['email']} vs {email}")
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "Content-Type",
                            "Access-Control-Allow-Methods": "POST, OPTIONS"
                        },
                        "body": json.dumps({
                            "error": "email_mismatch",
                            "message": "Email does not match the application"
                        })
                    }
                
                logger.info(f"Verified application {applicant_id} for auto-fill registration")
                
            except Exception as e:
                logger.error(f"Error verifying application: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Methods": "POST, OPTIONS"
                    },
                    "body": json.dumps({
                        "error": "application_verification_error",
                        "message": "Error verifying application"
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
                # Check if the existing registration is paid
                if existing_item["Item"].get("payment_status") == "paid":
                    logger.info(f"Duplicate registration attempt for paid user - email: {email}, course: {course_id}")
                    return {
                        "statusCode": 400,
                        "headers": {
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "Content-Type",
                            "Access-Control-Allow-Methods": "POST, OPTIONS"
                        },
                        "body": json.dumps({
                            "error": "email_already_registered",
                            "message": "This email has already been registered and paid for this course"
                        })
                    }
                else:
                    # If payment is pending, we'll overwrite the registration with new data
                    logger.info(f"Overwriting pending registration for email: {email}, course: {course_id}")
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
            "referral_source": "direct",
            "automation_interest": body.get("automation_interest", ""),
            "dietary_requirements": body["dietary_requirements"],
            "payment_status": "pending",
            "registration_date": timestamp,
            "stripe_session_id": "",  # Will be populated by webhook
        }
        
        table.put_item(Item=item)
        
        # Send CompleteRegistration event to Meta Conversions API with course type
        try:
            user_agent = event.get("headers", {}).get("User-Agent", "")
            user_data = {
                "email": email,
                "phone": body.get("phone", ""),
                "client_user_agent": user_agent
            }
            
            # Get the source URL from the event if available
            event_source_url = event.get("headers", {}).get("referer") or event.get("headers", {}).get("Referer")
            
            # Pass registration_type as 'course'
            meta_result = handle_complete_registration(user_data, event_source_url, registration_id, registration_type="course")
            if meta_result["success"]:
                logger.info(f"Meta Conversions API CompleteRegistration (course) event sent successfully for registration: {registration_id}")
            else:
                logger.warning(f"Failed to send Meta Conversions API event for registration: {registration_id}, error: {meta_result.get('error')}")
        except Exception as meta_error:
            logger.error(f"Error sending Meta Conversions API event: {str(meta_error)}")
            # Don't fail the registration if Meta API fails
        
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