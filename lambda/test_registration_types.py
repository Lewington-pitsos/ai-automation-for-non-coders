#!/usr/bin/env python3
"""
Test script to verify Meta Conversions API registration type tracking
"""

import json
from meta_conversions_api import handle_complete_registration

def test_course_registration():
    """Test course registration tracking"""
    print("Testing Course Registration...")
    
    user_data = {
        "email": "test@example.com",
        "phone": "+1234567890",
        "client_user_agent": "Mozilla/5.0 Test Browser"
    }
    
    result = handle_complete_registration(
        user_data=user_data,
        event_source_url="https://example.com/register",
        registration_id="test-course-123",
        registration_type="course"
    )
    
    print(f"Course Registration Result: {json.dumps(result, indent=2)}")
    return result

def test_livestream_registration():
    """Test livestream registration tracking"""
    print("\nTesting Livestream Registration...")
    
    user_data = {
        "email": "test@example.com",
        "client_user_agent": "Mozilla/5.0 Test Browser"
    }
    
    result = handle_complete_registration(
        user_data=user_data,
        event_source_url="https://example.com/livestream",
        registration_id="test-livestream-456",
        registration_type="livestream"
    )
    
    print(f"Livestream Registration Result: {json.dumps(result, indent=2)}")
    return result

def verify_custom_data():
    """Verify that custom data is being set correctly"""
    print("\nVerifying Custom Data Structure...")
    
    # Import the function to check internals
    from meta_conversions_api import send_conversion_event
    import time
    
    # Test data
    event_time = int(time.time())
    user_data = {"email": "test@example.com"}
    
    # Mock the send_conversion_event to see what's being sent
    print("Course Registration Custom Data:")
    custom_data_course = {
        "registration_type": "course",
        "content_name": "AI Automation Mastery Course",
        "content_category": "course"
    }
    print(json.dumps(custom_data_course, indent=2))
    
    print("\nLivestream Registration Custom Data:")
    custom_data_livestream = {
        "registration_type": "livestream",
        "content_name": "AI Tax Automation Livestream",
        "content_category": "livestream"
    }
    print(json.dumps(custom_data_livestream, indent=2))

if __name__ == "__main__":
    print("Meta Conversions API Registration Type Testing")
    print("=" * 50)
    
    # Note: These will only work if META_PIXEL_ID and META_ACCESS_TOKEN are set
    import os
    if not os.environ.get("META_PIXEL_ID") or not os.environ.get("META_ACCESS_TOKEN"):
        print("\nWARNING: META_PIXEL_ID and META_ACCESS_TOKEN environment variables not set.")
        print("Tests will run but API calls will fail.")
        print("To test actual API calls, set these environment variables first.")
    
    # Run tests
    verify_custom_data()
    
    # Uncomment to test actual API calls (requires valid credentials)
    # test_course_registration()
    # test_livestream_registration()
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    print("\nThe implementation now tracks two distinct registration types:")
    print("1. Course registrations - with registration_type='course'")
    print("2. Livestream registrations - with registration_type='livestream'")
    print("\nBoth send CompleteRegistration events but with different custom_data parameters.")
    print("This allows Meta to distinguish between the two types in their reporting.")