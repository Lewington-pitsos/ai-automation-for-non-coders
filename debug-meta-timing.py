#!/usr/bin/env python3
import requests
import json
import time
import hashlib
from datetime import datetime

PIXEL_ID = '1232612085335834'
ACCESS_TOKEN = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'
TEST_EVENT_CODE = 'TEST33140'

def hash_email(email):
    return hashlib.sha256(email.lower().encode()).hexdigest()

def send_debug_event():
    current_time = int(time.time())
    current_datetime = datetime.fromtimestamp(current_time)
    
    print(f"🕐 Current Unix timestamp: {current_time}")
    print(f"🕐 Current datetime: {current_datetime}")
    print(f"🕐 Sending event NOW...")
    
    url = f'https://graph.facebook.com/v21.0/{PIXEL_ID}/events'
    
    payload = {
        'data': [{
            'event_name': 'Contact',
            'event_time': current_time,
            'action_source': 'website',
            'user_data': {
                'em': [hash_email(f'debug.timing+{current_time}@example.com')],
                'client_user_agent': 'DEBUG-TIMING-TEST'
            },
            'custom_data': {
                'debug_message': f'Sent at {current_datetime} (timestamp: {current_time})'
            },
            'event_source_url': 'https://debug-timing-test.com'
        }],
        'test_event_code': TEST_EVENT_CODE
    }
    
    params = {'access_token': ACCESS_TOKEN}
    response = requests.post(url, json=payload, params=params)
    result = response.json()
    
    print(f"📤 Event sent with timestamp: {current_time}")
    print(f"📤 Event datetime: {current_datetime}")
    print(f"📤 Response: {result}")
    
    if 'events_received' in result:
        print(f"✅ SUCCESS! Event received by Meta")
        print(f"🔍 Check Events Manager > Test Events tab > Code: {TEST_EVENT_CODE}")
        print(f"🔍 Look for event with timestamp {current_time} or datetime {current_datetime}")
    else:
        print(f"❌ Error: {result}")

if __name__ == "__main__":
    send_debug_event()