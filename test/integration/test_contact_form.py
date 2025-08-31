#!/usr/bin/env python3
"""
Integration test for contact form endpoint
Tests the /contact API endpoint
"""

import json
import time
import requests
import sys
import os
from pathlib import Path

# Add parent directory to path for shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_terraform_outputs():
    """Load terraform outputs to get API URL"""
    outputs_path = Path(__file__).parent / 'terraform-outputs.json'
    
    if not outputs_path.exists():
        print("❌ terraform-outputs.json not found. Run deploy.sh first.")
        sys.exit(1)
    
    with open(outputs_path, 'r') as f:
        outputs = json.load(f)
    
    return outputs

def test_contact_endpoint():
    """Test the contact form endpoint"""
    outputs = load_terraform_outputs()
    
    # Get API URL from terraform outputs
    api_url = outputs['api_gateway_invoke_url']['value']
    contact_endpoint = f"{api_url}/contact"
    
    print(f"🧪 Testing contact form endpoint: {contact_endpoint}")
    print("-" * 50)
    
    # Test 1: Valid contact form submission
    print("\n✅ Test 1: Valid contact form submission")
    valid_payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "message": "This is a test message from the integration test suite. Please ignore this message."
    }
    
    try:
        response = requests.post(
            contact_endpoint,
            json=valid_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ Status code: {response.status_code}")
            data = response.json()
            if 'messageId' in data:
                print(f"  ✓ Email sent successfully. MessageId: {data['messageId']}")
            else:
                print(f"  ✓ Response: {data}")
        else:
            print(f"  ✗ Unexpected status code: {response.status_code}")
            print(f"  ✗ Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 2: Missing required field (name)
    print("\n✅ Test 2: Missing name field")
    invalid_payload = {
        "email": "testuser@example.com",
        "message": "Test message"
    }
    
    try:
        response = requests.post(
            contact_endpoint,
            json=invalid_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected with status: {response.status_code}")
            data = response.json()
            if 'error' in data and 'name' in data['error'].lower():
                print(f"  ✓ Error message mentions missing name: {data['error']}")
            else:
                print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have returned 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 3: Missing email field
    print("\n✅ Test 3: Missing email field")
    invalid_payload = {
        "name": "Test User",
        "message": "Test message"
    }
    
    try:
        response = requests.post(
            contact_endpoint,
            json=invalid_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected with status: {response.status_code}")
            data = response.json()
            if 'error' in data and 'email' in data['error'].lower():
                print(f"  ✓ Error message mentions missing email: {data['error']}")
            else:
                print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have returned 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 4: Missing message field
    print("\n✅ Test 4: Missing message field")
    invalid_payload = {
        "name": "Test User",
        "email": "testuser@example.com"
    }
    
    try:
        response = requests.post(
            contact_endpoint,
            json=invalid_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected with status: {response.status_code}")
            data = response.json()
            if 'error' in data and 'message' in data['error'].lower():
                print(f"  ✓ Error message mentions missing message: {data['error']}")
            else:
                print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have returned 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 5: Empty body
    print("\n✅ Test 5: Empty request body")
    
    try:
        response = requests.post(
            contact_endpoint,
            data='',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected with status: {response.status_code}")
            data = response.json()
            print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have returned 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 6: Invalid JSON
    print("\n✅ Test 6: Invalid JSON")
    
    try:
        response = requests.post(
            contact_endpoint,
            data='{"name": "Test", invalid json}',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected with status: {response.status_code}")
            data = response.json()
            print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have returned 400, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    # Test 7: CORS preflight (OPTIONS)
    print("\n✅ Test 7: CORS preflight request")
    
    try:
        response = requests.options(
            contact_endpoint,
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ CORS preflight successful: {response.status_code}")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            for header, value in cors_headers.items():
                if value:
                    print(f"  ✓ {header}: {value}")
        else:
            print(f"  ✗ Unexpected status code for OPTIONS: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ OPTIONS request failed: {str(e)}")
        return False
    
    # Test 8: Whitespace-only fields
    print("\n✅ Test 8: Whitespace-only fields")
    whitespace_payload = {
        "name": "   ",
        "email": "test@example.com",
        "message": "\n\t  \n"
    }
    
    try:
        response = requests.post(
            contact_endpoint,
            json=whitespace_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 400:
            print(f"  ✓ Correctly rejected whitespace-only fields: {response.status_code}")
            data = response.json()
            print(f"  ✓ Error response: {data}")
        else:
            print(f"  ✗ Should have rejected whitespace-only fields, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Request failed: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All contact form tests passed!")
    return True

def main():
    """Main test runner"""
    print("\n🚀 Contact Form Integration Tests")
    print("=" * 50)
    
    # Check if API is reachable first
    outputs = load_terraform_outputs()
    api_url = outputs['api_gateway_invoke_url']['value']
    
    print(f"📡 API URL: {api_url}")
    
    # Run tests
    success = test_contact_endpoint()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()