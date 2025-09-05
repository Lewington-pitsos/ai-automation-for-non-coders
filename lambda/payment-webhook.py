import json
import boto3
import os
import stripe
import logging
from datetime import datetime
from decimal import Decimal
from email_templates import get_user_confirmation_email
from meta_conversions_api import handle_purchase

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("TABLE_NAME", "course_registrations"))
ses_client = boto3.client("ses")

stripe.api_key = os.environ.get("STRIPE_API_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
from_email = os.environ.get("FROM_EMAIL")
admin_email = os.environ.get("ADMIN_EMAIL")

def lambda_handler(event, context):
    try:
        # Handle base64 encoded body from API Gateway
        payload = event["body"]
        if event.get("isBase64Encoded", False):
            import base64
            payload = base64.b64decode(payload).decode('utf-8')
        
        # Get signature header (try both cases)
        sig_header = (event["headers"].get("Stripe-Signature") or 
                     event["headers"].get("stripe-signature"))
        
        if not sig_header:
            logger.error("Missing Stripe-Signature header")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing signature header"})
            }
        
        stripe_event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
        
        if stripe_event["type"] == "checkout.session.completed":
            session = stripe_event["data"]["object"]
            customer_email = session.get("customer_details", {}).get("email", "").lower()
            client_reference_id = session.get("client_reference_id")
            
            # Try to get registration by ID from client_reference_id first
            if client_reference_id:
                try:
                    # Query using the GSI on registration_id
                    response = table.query(
                        IndexName="registration-id-index",
                        KeyConditionExpression="registration_id = :reg_id",
                        ExpressionAttributeValues={":reg_id": client_reference_id}
                    )
                    
                    if response["Items"]:
                        item = response["Items"][0]
                        course_id = item["course_id"]
                        registration_id = item["registration_id"]
                        
                        logger.info(f"Found registration by ID: {registration_id}")
                    else:
                        logger.error(f"No registration found for ID: {client_reference_id}")
                        return {
                            "statusCode": 404,
                            "body": json.dumps({"error": "Registration not found"})
                        }
                except Exception as e:
                    logger.error(f"Error querying by registration ID: {str(e)}")
                    return {
                        "statusCode": 500,
                        "body": json.dumps({"error": "Database query failed"})
                    }
            else:
                # Fallback: try to find by email (less reliable)
                logger.warning("No client_reference_id found, falling back to email lookup")
                course_id = "01_ai_automation_for_non_coders"  # Default
                
                try:
                    response = table.get_item(
                        Key={
                            "course_id": course_id,
                            "email": customer_email
                        }
                    )
                    
                    if "Item" in response:
                        item = response["Item"]
                        registration_id = item["registration_id"]
                    else:
                        logger.error(f"No registration found for email: {customer_email}")
                        return {
                            "statusCode": 404,
                            "body": json.dumps({"error": "Registration not found"})
                        }
                except Exception as e:
                    logger.error(f"Error querying by email: {str(e)}")
                    return {
                        "statusCode": 500,
                        "body": json.dumps({"error": "Database query failed"})
                    }

            # Update the registration with payment information
            table.update_item(
                Key={
                    "course_id": course_id,
                    "email": item["email"]  # Use the email from the found item
                },
                UpdateExpression="SET payment_status = :status, payment_date = :date, stripe_session_id = :session_id, amount_paid = :amount",
                ExpressionAttributeValues={
                    ":status": "paid",
                    ":date": datetime.utcnow().isoformat(),
                    ":session_id": session.get("id", ""),
                    ":amount": Decimal(str(session.get("amount_total", 0))) / Decimal("100")  # Convert from cents to dollars
                }
            )
            
            # Send confirmation email to user
            amount_paid = session.get("amount_total", 0) / 100
            subject, html_body, text_body = get_user_confirmation_email(item["name"], registration_id, amount_paid)
            
            ses_client.send_email(
                Source=from_email,
                Destination={"ToAddresses": [item["email"]]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {
                        "Html": {
                            "Data": html_body
                        },
                        "Text": {
                            "Data": text_body
                        }
                    }
                }
            )
            
            # Send notification email to admin
            ses_client.send_email(
                Source=from_email,
                Destination={"ToAddresses": [admin_email]},
                Message={
                    "Subject": {"Data": "New Course Registration Payment"},
                    "Body": {
                        "Text": {
                            "Data": f"""New payment received:

Name: {item["name"]}
Email: {item["email"]}
Registration ID: {registration_id}
Amount: $${session.get("amount_total", 0) / 100:.2f}
Stripe Session ID: {session.get("id", "")}"""
                        }
                    }
                }
            )
            
            # Send Purchase event to Meta Conversions API
            try:
                user_data = {
                    "email": item["email"],
                    "phone": item.get("phone", "")
                }
                
                purchase_data = {
                    "currency": "USD",
                    "value": float(session.get("amount_total", 0) / 100)
                }
                
                meta_result = handle_purchase(user_data, purchase_data, None, registration_id)
                if meta_result["success"]:
                    logger.info(f"Meta Conversions API Purchase event sent successfully for registration: {registration_id}")
                else:
                    logger.warning(f"Failed to send Meta Conversions API Purchase event for registration: {registration_id}, error: {meta_result.get('error')}")
            except Exception as meta_error:
                logger.error(f"Error sending Meta Conversions API Purchase event: {str(meta_error)}")
                # Don't fail the webhook if Meta API fails
            
            logger.info(f"Payment successful for registration: {registration_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({"received": True})
        }
        
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid payload"})
        }
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid signature"})
        }
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }