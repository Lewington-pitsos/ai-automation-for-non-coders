#!/usr/bin/env python3
import requests
import json
import time
import sys
import hashlib
from datetime import datetime

# Meta Test Events configuration
TEST_EVENT_CODE = 'TEST33140'  # Same test code as your working test
PIXEL_ID = '1232612085335834'
ACCESS_TOKEN = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

# Your API Gateway endpoints
API_BASE_URL = 'https://0rhn8rbzd4.execute-api.ap-southeast-2.amazonaws.com/prod'
ENDPOINTS = {
    'registration': f'{API_BASE_URL}/register',
    'contact': f'{API_BASE_URL}/contact',
    'view_content': f'{API_BASE_URL}/view-content',
    'payment': f'{API_BASE_URL}/payment-webhook'
}

def hash_email(email):
    """Hash email for Meta API"""
    return hashlib.sha256(email.lower().encode()).hexdigest()

def send_test_mode_event(event_name, test_data):
    """Send a test event directly to Meta to enable test mode"""
    url = f'https://graph.facebook.com/v21.0/{PIXEL_ID}/events'
    
    # Hash user data properly
    user_data = test_data.get('user_data', {})
    hashed_user_data = {}
    if user_data.get('email'):
        hashed_user_data['em'] = [hash_email(user_data['email'])]
    if user_data.get('phone'):
        hashed_user_data['ph'] = [hashlib.sha256(user_data['phone'].encode()).hexdigest()]
    if user_data.get('client_user_agent'):
        hashed_user_data['client_user_agent'] = user_data['client_user_agent']
    
    payload = {
        'data': [{
            'event_name': event_name,
            'event_time': int(time.time()),
            'action_source': 'website',
            'user_data': hashed_user_data,
            'custom_data': test_data.get('custom_data', {}),
            'event_source_url': test_data.get('event_source_url', 'https://your-website.com')
        }],
        'test_event_code': TEST_EVENT_CODE
    }
    
    params = {'access_token': ACCESS_TOKEN}
    response = requests.post(url, json=payload, params=params)
    return response.json()

def test_registration_event():
    """Test registration Lambda endpoint"""
    print("\n📝 Testing Registration Event...")
    
    # Sample registration data matching your Lambda requirements
    test_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test.user+{int(time.time())}@example.com",
        "phone": "+12025551234",
        "course_id": "01_ai_automation_for_non_coders",
        "referral_source": "google",
        "dietary_requirements": "none",
        "client_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    
    try:
        # Send to your backend
        response = requests.post(ENDPOINTS['registration'], json=test_data, timeout=10)
        print(f"Backend Response Status: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        
        # Also send test event directly to Meta for verification
        meta_test = send_test_mode_event('CompleteRegistration', {
            'user_data': {
                'em': [test_data['email']],
                'ph': [test_data['phone']],
                'client_user_agent': test_data['client_user_agent']
            },
            'event_source_url': 'https://your-website.com/register'
        })
        print(f"Direct Meta Test Response: {meta_test}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_contact_event():
    """Test contact Lambda endpoint"""
    print("\n✉️ Testing Contact Event...")
    
    test_data = {
        "name": "Test Contact",
        "email": f"test.contact+{int(time.time())}@example.com",
        "message": "This is a test contact message",
        "client_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        # Send to your backend
        response = requests.post(ENDPOINTS['contact'], json=test_data, timeout=10)
        print(f"Backend Response Status: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        
        # Also send test event directly to Meta
        meta_test = send_test_mode_event('Contact', {
            'user_data': {
                'em': [test_data['email']],
                'client_user_agent': test_data['client_user_agent']
            },
            'event_source_url': 'https://your-website.com/contact'
        })
        print(f"Direct Meta Test Response: {meta_test}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_view_content_event():
    """Test view content Lambda endpoint"""
    print("\n👁️ Testing View Content Event...")
    
    test_data = {
        "event_type": "ViewContent",
        "user_data": {
            "email": f"viewer+{int(time.time())}@example.com",
            "client_user_agent": "Mozilla/5.0 (X11; Linux x86_64)"
        },
        "event_source_url": "https://your-website.com/course/python-basics",
        "custom_data": {
            "content_name": "Python Basics Course",
            "content_category": "Programming",
            "value": 99.00,
            "currency": "USD"
        }
    }
    
    try:
        # Send to your backend
        response = requests.post(ENDPOINTS['view_content'], json=test_data, timeout=10)
        print(f"Backend Response Status: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        
        # Also send test event directly to Meta
        meta_test = send_test_mode_event('ViewContent', test_data)
        print(f"Direct Meta Test Response: {meta_test}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def test_purchase_event():
    """Test purchase/payment webhook endpoint"""
    print("\n💳 Testing Purchase Event...")
    
    # Simulate a Stripe webhook payload
    test_data = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_test_{int(time.time())}",
                "customer_email": f"buyer+{int(time.time())}@example.com",
                "amount_total": 9900,  # Amount in cents
                "currency": "usd",
                "metadata": {
                    "course": "Python Advanced"
                }
            }
        }
    }
    
    try:
        # Send to your backend
        response = requests.post(ENDPOINTS['payment'], json=test_data, timeout=10)
        print(f"Backend Response Status: {response.status_code}")
        print(f"Backend Response: {response.json()}")
        
        # Also send test event directly to Meta
        meta_test = send_test_mode_event('Purchase', {
            'user_data': {
                'em': [test_data['data']['object']['customer_email']],
            },
            'custom_data': {
                'value': 99.00,
                'currency': 'USD'
            },
            'event_source_url': 'https://your-website.com/checkout'
        })
        print(f"Direct Meta Test Response: {meta_test}")
        
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("META CONVERSIONS API BACKEND TESTING")
    print("=" * 60)
    print(f"Test Event Code: {TEST_EVENT_CODE}")
    print(f"Pixel ID: {PIXEL_ID}")
    print(f"API Base URL: {API_BASE_URL}")
    print("\n⚠️  IMPORTANT: Update API_BASE_URL with your actual API Gateway URL")
    print("=" * 60)
    
    if API_BASE_URL == 'https://your-api-gateway-url.execute-api.region.amazonaws.com/prod':
        print("\n❌ Please update the API_BASE_URL variable with your actual API Gateway URL")
        print("You can find this in AWS Console > API Gateway > Your API > Stages > prod")
        sys.exit(1)
    
    print("\nStarting tests...")
    print("\nNOTE: After running tests, check Meta Events Manager:")
    print("1. Go to Events Manager")
    print("2. Click on 'course website' pixel")
    print("3. Click 'Test events' tab")
    print(f"4. Enter code: {TEST_EVENT_CODE}")
    print("5. You should see both direct test events AND backend-generated events")
    print("=" * 60)
    
    # Run tests
    tests = [
        ("Registration", test_registration_event),
        ("Contact", test_contact_event),
        ("View Content", test_view_content_event),
        ("Purchase", test_purchase_event)
    ]
    
    results = []
    for test_name, test_func in tests:
        time.sleep(2)  # Small delay between tests
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Check Meta Events Manager Test Events tab")
    print(f"2. Use test code: {TEST_EVENT_CODE}")
    print("3. Verify you see events from both:")
    print("   - Direct API calls (marked as 'Manual setup')")
    print("   - Your Lambda backend (marked as 'Server')")
    print("4. Check the event details match your test data")
    print("=" * 60)

if __name__ == "__main__":
    main()