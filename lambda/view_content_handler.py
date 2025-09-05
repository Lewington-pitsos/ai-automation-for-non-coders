import json
import logging
import os
from meta_conversions_api import handle_view_content

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda handler for ViewContent events from the frontend
    
    Expected event structure:
    {
        "user_data": {
            "email": "user@example.com",  // Optional
            "client_user_agent": "Mozilla/5.0..."
        },
        "event_source_url": "https://example.com/page",
        "content_data": {
            "content_name": "Course Landing Page",
            "content_category": "education"
        }
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
        
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", {})
        
        # Get user data from request or headers
        user_data = body.get("user_data", {})
        
        # Get User-Agent from headers if not in user_data
        if not user_data.get("client_user_agent"):
            user_data["client_user_agent"] = event.get("headers", {}).get("User-Agent", "")
        
        # Get event source URL
        event_source_url = body.get("event_source_url") or event.get("headers", {}).get("referer") or event.get("headers", {}).get("Referer")
        
        # Get content data
        content_data = body.get("content_data", {})
        
        if not event_source_url:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "event_source_url is required"})
            }
        
        # Send ViewContent event to Meta Conversions API
        try:
            meta_result = handle_view_content(user_data, event_source_url, content_data)
            
            if meta_result["success"]:
                logger.info(f"Meta Conversions API ViewContent event sent successfully for URL: {event_source_url}")
                return {
                    "statusCode": 200,
                    "headers": headers,
                    "body": json.dumps({
                        "message": "ViewContent event sent successfully",
                        "event_id": meta_result["event_id"]
                    })
                }
            else:
                logger.warning(f"Failed to send Meta Conversions API ViewContent event for URL: {event_source_url}, error: {meta_result.get('error')}")
                return {
                    "statusCode": 500,
                    "headers": headers,
                    "body": json.dumps({
                        "error": "Failed to send ViewContent event",
                        "details": meta_result.get("error")
                    })
                }
        except Exception as meta_error:
            logger.error(f"Error sending Meta Conversions API ViewContent event: {str(meta_error)}")
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({"error": "Internal server error"})
            }
    
    except Exception as e:
        logger.error(f"Error in ViewContent handler: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal server error"})
        }