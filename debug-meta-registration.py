#!/usr/bin/env python3
import requests
import json
import time
import hashlib
from datetime import datetime

# Meta API configuration  
PIXEL_ID = '1232612085335834'
ACCESS_TOKEN = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

def hash_email(email):
    return hashlib.sha256(email.lower().encode()).hexdigest()

def send_registration_event_like_lambda():
    """Send exactly what the Lambda would send for CompleteRegistration"""
    current_time = int(time.time())
    
    print(f"🕐 Sending CompleteRegistration event at: {datetime.fromtimestamp(current_time)}")
    print(f"🔢 Unix timestamp: {current_time}")
    
    # Replicate exact Lambda logic
    user_data = {
        "em": [hash_email("lewingtonpitsos@gmail.com")],  # Your email from logs
        "client_user_agent": "DEBUG-Lambda-Replication"
    }
    
    event_data = {
        "event_name": "CompleteRegistration", 
        "event_time": current_time,
        "action_source": "website",
        "user_data": user_data,
        "event_id": f"registration_debug_{current_time}"
    }
    
    # Send as PRODUCTION event (like your Lambda does)
    payload = {
        "data": [event_data],
        "access_token": ACCESS_TOKEN
    }
    
    url = f'https://graph.facebook.com/v21.0/{PIXEL_ID}/events'
    
    print(f"📤 Sending to Meta (PRODUCTION mode)...")
    print(f"📤 Event data: {json.dumps(event_data, indent=2)}")
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"📥 Meta response: {result}")
    
    if 'events_received' in result:
        print(f"✅ SUCCESS! {result['events_received']} event(s) received")
        print(f"🔍 Event should appear in Events Manager > Overview tab (NOT Test Events)")
        print(f"🔍 Look for CompleteRegistration event at {datetime.fromtimestamp(current_time)}")
        print(f"🔍 fbtrace_id: {result.get('fbtrace_id')}")
        return True
    else:
        print(f"❌ Error: {result}")
        return False

def send_test_registration():
    """Send same event but in TEST mode"""
    current_time = int(time.time())
    
    print(f"\n🧪 Now sending TEST version...")
    
    user_data = {
        "em": [hash_email("lewingtonpitsos@gmail.com")],
        "client_user_agent": "DEBUG-Test-Mode"
    }
    
    event_data = {
        "event_name": "CompleteRegistration",
        "event_time": current_time,  
        "action_source": "website",
        "user_data": user_data,
        "event_id": f"test_registration_{current_time}"
    }
    
    # Send as TEST event
    payload = {
        "data": [event_data],
        "access_token": ACCESS_TOKEN,
        "test_event_code": "TEST33140"  # Add test code
    }
    
    url = f'https://graph.facebook.com/v21.0/{PIXEL_ID}/events'
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    print(f"📥 Test response: {result}")
    
    if 'events_received' in result:
        print(f"✅ TEST SUCCESS! {result['events_received']} event(s) received") 
        print(f"🔍 Should appear in Test Events tab with code TEST33140")
        return True
    else:
        print(f"❌ Test error: {result}")
        return False

def main():
    print("=" * 60)
    print("META REGISTRATION EVENT DEBUG")
    print("=" * 60)
    
    # Send production event like Lambda
    prod_success = send_registration_event_like_lambda()
    
    # Send test event for comparison
    test_success = send_test_registration()
    
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")  
    print("=" * 60)
    print(f"Production event (like Lambda): {'✅ SUCCESS' if prod_success else '❌ FAILED'}")
    print(f"Test event: {'✅ SUCCESS' if test_success else '❌ FAILED'}")
    
    if prod_success and test_success:
        print(f"\n🔍 Both succeeded! Check:")
        print(f"   - Test Events tab (code TEST33140) - should show immediately")
        print(f"   - Overview tab - production event (may have delay)")
        print(f"\n🕐 If production events are delayed, the issue is Meta's processing lag")
        print(f"   Your Lambda integration is working correctly!")
    elif not prod_success:
        print(f"\n❌ Production event failed - this explains the delay!")
        print(f"   Your Lambda might be sending malformed data")

if __name__ == "__main__":
    main()