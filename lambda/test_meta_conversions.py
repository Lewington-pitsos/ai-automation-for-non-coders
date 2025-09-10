#!/usr/bin/env python3
"""
Test script for Meta Conversions API integration
Run this to test the Meta Conversions API functions before deployment
"""

import sys
import os
import json
from unittest.mock import Mock, patch

# Add current directory to path for importing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock environment variables
os.environ["META_PIXEL_ID"] = "123456789"
os.environ["META_ACCESS_TOKEN"] = "xxx"

# Import after setting environment variables
from meta_conversions_api import (
    handle_complete_registration,
    handle_contact,
    handle_purchase,
    hash_data
)

def test_hash_data():
    """Test data hashing function"""
    print("Testing hash_data function...")
    
    # Test email hashing
    email = "test@example.com"
    hashed = hash_data(email)
    expected = "973dfe463ec85785f5f95af5ba3906eedb2d931c24e69824a89ea65dba4e813b"
    
    assert hashed == expected, f"Expected {expected}, got {hashed}"
    
    # Test case insensitivity
    assert hash_data("TEST@EXAMPLE.COM") == hash_data("test@example.com")
    
    # Test None/empty handling
    assert hash_data(None) is None
    assert hash_data("") is None
    
    print("✓ hash_data tests passed")

def test_event_payload_structure():
    """Test that event payloads have correct structure"""
    print("Testing event payload structure...")
    
    with patch('meta_conversions_api.requests.post') as mock_post:
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"events_received": 1}
        mock_post.return_value = mock_response
        
        # Test CompleteRegistration event
        user_data = {
            "email": "test@example.com",
            "phone": "+1234567890",
            "client_user_agent": "Mozilla/5.0 Test"
        }
        
        result = handle_complete_registration(
            user_data=user_data,
            event_source_url="https://example.com/register",
            registration_id="reg_123"
        )
        
        assert result["success"] == True
        assert "event_id" in result
        
        # Verify the API call was made with correct payload
        assert mock_post.called
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        
        assert "data" in payload
        assert len(payload["data"]) == 1
        
        event_data = payload["data"][0]
        assert event_data["event_name"] == "CompleteRegistration"
        assert event_data["action_source"] == "website"
        assert event_data["event_id"] == "registration_reg_123"
        assert event_data["event_source_url"] == "https://example.com/register"
        
        # Check user_data hashing
        assert "user_data" in event_data
        user_data_sent = event_data["user_data"]
        assert "em" in user_data_sent
        assert user_data_sent["em"][0] == hash_data("test@example.com")
        assert "ph" in user_data_sent
        assert user_data_sent["ph"][0] == hash_data("+1234567890")
        assert user_data_sent["client_user_agent"] == "Mozilla/5.0 Test"
        
        print("✓ CompleteRegistration event structure is correct")

def test_contact_event():
    """Test Contact event"""
    print("Testing Contact event...")
    
    with patch('meta_conversions_api.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"events_received": 1}
        mock_post.return_value = mock_response
        
        user_data = {
            "email": "contact@example.com",
            "phone": "+1234567890"
        }
        
        result = handle_contact(
            user_data=user_data,
            event_source_url="https://example.com/contact"
        )
        
        assert result["success"] == True
        
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        event_data = payload["data"][0]
        
        assert event_data["event_name"] == "Contact"
        assert "contact_contact@example.com_" in event_data["event_id"]
        
        print("✓ Contact event structure is correct")

def test_purchase_event():
    """Test Purchase event"""
    print("Testing Purchase event...")
    
    with patch('meta_conversions_api.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"events_received": 1}
        mock_post.return_value = mock_response
        
        user_data = {
            "email": "buyer@example.com",
            "phone": "+1234567890"
        }
        
        purchase_data = {
            "currency": "USD",
            "value": 299.99
        }
        
        result = handle_purchase(
            user_data=user_data,
            purchase_data=purchase_data,
            event_source_url="https://example.com/success",
            order_id="order_789"
        )
        
        assert result["success"] == True
        
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        event_data = payload["data"][0]
        
        assert event_data["event_name"] == "Purchase"
        assert event_data["event_id"] == "purchase_order_789"
        assert "custom_data" in event_data
        assert event_data["custom_data"]["currency"] == "USD"
        assert event_data["custom_data"]["value"] == 299.99
        
        print("✓ Purchase event structure is correct")

def test_api_error_handling():
    """Test API error handling"""
    print("Testing API error handling...")
    
    with patch('meta_conversions_api.requests.post') as mock_post:
        # Mock API error
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        user_data = {"email": "test@example.com"}
        
        result = handle_complete_registration(user_data)
        
        assert result["success"] == False
        assert "error" in result
        assert result["error"] == "Network error"
        
        print("✓ Error handling works correctly")

def main():
    """Run all tests"""
    print("🧪 Starting Meta Conversions API tests...\n")
    
    try:
        test_hash_data()
        test_event_payload_structure()
        test_contact_event()
        test_purchase_event()
        test_view_content_event()
        test_api_error_handling()
        
        print("\n✅ All tests passed! Meta Conversions API integration is ready.")
        print("\n📝 Next steps:")
        print("1. Deploy the Lambda functions with the updated code")
        print("2. Set the META_PIXEL_ID environment variable on your Lambda functions")
        print("3. Set the META_ACCESS_TOKEN environment variable securely")
        print("4. Update your API Gateway endpoints")
        print("5. Update the meta-tracking.js file with your actual API endpoints")
        print("6. Include meta-tracking.js in your HTML pages")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()