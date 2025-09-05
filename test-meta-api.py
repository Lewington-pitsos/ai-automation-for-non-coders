import requests
import time

# CORRECT PIXEL ID
pixel_id = '1232612085335834'  # Your course website pixel
access_token = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

# Prepare test event for WEBSITE pixel
event_data = {
    'data': [{
        'event_name': 'TestEvent',
        'event_time': int(time.time()),
        'action_source': 'website',  # Changed to website
        'user_data': {
            'client_ip_address': '192.168.1.1',
            'client_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        },
        'event_source_url': 'https://your-website.com/test-page',
        'custom_data': {
            'test_parameter': 'API test',
            'currency': 'USD',
            'value': 99.00
        }
    }],
    'test_event_code': 'TEST33140'  # Use this code in Test Events tab
}

# Send the request
url = f'https://graph.facebook.com/v21.0/{pixel_id}/events'
params = {'access_token': access_token}

print(f"Sending test event to Pixel {pixel_id}...")
response = requests.post(url, json=event_data, params=params)

# Check response
result = response.json()
print("\nResponse:", result)

if 'events_received' in result:
    print(f"✅ Success! {result['events_received']} event(s) received")
    print("\nNext steps:")
    print("1. Go to Events Manager")
    print("2. Click on 'course website' pixel")
    print("3. Click 'Test events' tab")
    print("4. Enter code: TEST33140")
else:
    print("❌ Error:", result)