import json
import os
import logging
import hashlib
import time
import uuid
import requests
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Meta Conversions API configuration
META_PIXEL_ID = os.environ.get("META_PIXEL_ID", "1232612085335834")
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "xxx")
TEST_EVENT_CODE = os.environ.get("META_TEST_EVENT_CODE")  # Optional: for testing
API_VERSION = "v21.0"
CONVERSIONS_API_URL = f"https://graph.facebook.com/{API_VERSION}/{META_PIXEL_ID}/events"

def hash_data(data):
    """Hash user data for privacy compliance"""
    if not data:
        return None
    return hashlib.sha256(data.lower().encode()).hexdigest()

def send_conversion_event(event_name, event_time, user_data, custom_data=None, event_source_url=None, event_id=None, test_event_code=None):
    """
    Send conversion event to Meta Conversions API
    
    Args:
        event_name: Standard event name (e.g., CompleteRegistration, Contact, ViewContent)
        event_time: Unix timestamp of when event occurred
        user_data: Dictionary with user information (email, phone, etc.)
        custom_data: Additional event data (e.g., value, currency)
        event_source_url: URL where the event occurred
        event_id: Unique identifier for deduplication
    """
    
    # Generate event ID if not provided
    if not event_id:
        event_id = str(uuid.uuid4())
    
    # Prepare user data with hashing
    hashed_user_data = {}
    if user_data.get("email"):
        hashed_user_data["em"] = [hash_data(user_data["email"])]
    if user_data.get("phone"):
        hashed_user_data["ph"] = [hash_data(user_data["phone"])]
    if user_data.get("client_user_agent"):
        hashed_user_data["client_user_agent"] = user_data["client_user_agent"]
    
    # Build event payload
    event_data = {
        "event_name": event_name,
        "event_time": int(event_time),
        "action_source": "website",
        "user_data": hashed_user_data,
        "event_id": event_id
    }
    
    if event_source_url:
        event_data["event_source_url"] = event_source_url
    
    if custom_data:
        event_data["custom_data"] = custom_data
    
    payload = {
        "data": [event_data],
        "access_token": META_ACCESS_TOKEN
    }
    
    # Add test event code if provided
    if test_event_code:
        payload["test_event_code"] = test_event_code
    
    try:
        response = requests.post(CONVERSIONS_API_URL, json=payload)
        response.raise_for_status()
        
        logger.info(f"Successfully sent {event_name} event to Meta Conversions API. Event ID: {event_id}")
        return {"success": True, "event_id": event_id, "response": response.json()}
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send {event_name} event to Meta Conversions API: {str(e)}")
        return {"success": False, "error": str(e)}

def handle_complete_registration(user_data, event_source_url=None, registration_id=None, registration_type="course"):
    """
    Handle Complete Registration event with type distinction
    
    Args:
        user_data: User information dictionary
        event_source_url: URL where registration occurred
        registration_id: Unique registration ID
        registration_type: Type of registration ('course' or 'livestream')
    """
    event_time = int(time.time())
    # Use registration_id as event_id for deduplication
    event_id = f"registration_{registration_id}" if registration_id else None
    
    # Add custom data to distinguish registration types
    custom_data = {
        "registration_type": registration_type,
        "content_name": "AI Tax Automation Livestream" if registration_type == "livestream" else "AI Automation Mastery Course",
        "content_category": registration_type
    }
    
    return send_conversion_event(
        event_name="CompleteRegistration",
        event_time=event_time,
        user_data=user_data,
        custom_data=custom_data,
        event_source_url=event_source_url,
        event_id=event_id,
        test_event_code=TEST_EVENT_CODE
    )

def handle_contact(user_data, event_source_url=None, contact_id=None):
    """Handle Contact event"""
    event_time = int(time.time())
    # Generate unique event_id for contact events
    event_id = f"contact_{contact_id}_{int(time.time())}" if contact_id else f"contact_{user_data.get('email', 'unknown')}_{int(time.time())}"
    return send_conversion_event(
        event_name="Contact",
        event_time=event_time,
        user_data=user_data,
        event_source_url=event_source_url,
        event_id=event_id,
        test_event_code=TEST_EVENT_CODE
    )


def handle_purchase(user_data, purchase_data, event_source_url=None, order_id=None):
    """Handle Purchase event"""
    event_time = int(time.time())
    custom_data = {
        "currency": purchase_data.get("currency", "USD"),
        "value": purchase_data.get("value", 0)
    }
    # Use order_id for deduplication
    event_id = f"purchase_{order_id}" if order_id else f"purchase_{user_data.get('email', 'unknown')}_{int(time.time())}"
    return send_conversion_event(
        event_name="Purchase",
        event_time=event_time,
        user_data=user_data,
        custom_data=custom_data,
        event_source_url=event_source_url,
        event_id=event_id,
        test_event_code=TEST_EVENT_CODE
    )

def lambda_handler(event, context):
    """
    Lambda handler for Meta Conversions API events
    
    Expected event structure:
    {
        "event_type": "CompleteRegistration|Contact|ViewContent|Purchase",
        "user_data": {
            "email": "user@example.com",
            "phone": "+1234567890",
            "client_user_agent": "Mozilla/5.0..."
        },
        "event_source_url": "https://example.com/register",
        "custom_data": {...}  // Optional, for Purchase events
    }
    """
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS"
    }
    
    try:
        # Handle OPTIONS for CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "CORS preflight"})
            }
        
        # Validate environment variables
        if not META_PIXEL_ID or not META_ACCESS_TOKEN:
            logger.error("Missing required environment variables: META_PIXEL_ID or META_ACCESS_TOKEN")
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "Server configuration error"})
            }
        
        # Parse request body
        if isinstance(event, dict) and "body" in event:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            body = event
        
        event_type = body.get("event_type")
        user_data = body.get("user_data", {})
        event_source_url = body.get("event_source_url")
        custom_data = body.get("custom_data")
        
        if not event_type:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "event_type is required"})
            }
        
        if not user_data.get("email"):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "user_data.email is required"})
            }
        
        # Route to appropriate handler
        result = None
        if event_type == "CompleteRegistration":
            # Get registration type from custom data if provided
            registration_type = custom_data.get("registration_type", "course") if custom_data else "course"
            result = handle_complete_registration(user_data, event_source_url, registration_type=registration_type)
        elif event_type == "Contact":
            result = handle_contact(user_data, event_source_url)
        elif event_type == "Purchase":
            if not custom_data or not custom_data.get("value"):
                return {
                    "statusCode": 400,
                    "headers": headers,
                    "body": json.dumps({"error": "custom_data with value is required for Purchase events"})
                }
            result = handle_purchase(user_data, custom_data, event_source_url)
        else:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": f"Unsupported event_type: {event_type}"})
            }
        
        if result["success"]:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "message": "Event sent successfully",
                    "event_id": result["event_id"]
                })
            }
        else:
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "error": "Failed to send event to Meta Conversions API",
                    "details": result["error"]
                })
            }
    
    except Exception as e:
        logger.error(f"Error in Meta Conversions API handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal server error"})
        }