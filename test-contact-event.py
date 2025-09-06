import requests
import time
import uuid

# CORRECT PIXEL ID
pixel_id = '1232612085335834'  # Your course website pixel
access_token = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

test_event_code = 'TEST62526'

# Generate unique event data each time
current_time = int(time.time())
unique_id = str(uuid.uuid4())

# Prepare test Contact event for WEBSITE pixel
event_data = {
    'data': [{
        'event_name': 'Contact',
        'event_time': current_time,
        'action_source': 'website',
        'user_data': {
            'client_ip_address': '192.168.1.1',
            'client_user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'em': ['7c4a8d09ca3762af61e59520943dc26494f8941b00d8e5b3acbc4e4c3e3bb462'],  # hashed email for test@example.com
            'ph': ['f660ab912ec121d1b1e928a0bb4bc61b15f5ad44d5efdc4e1c92a25e99b8e44a']   # hashed phone for +1234567890
        },
        'event_source_url': 'https://your-website.com/contact',
        'event_id': f'contact_test_{unique_id}',
        'custom_data': {
            'contact_method': 'contact_form',
            'message_length': 150
        }
    }],
    'test_event_code': test_event_code
}

# Send the request
url = f'https://graph.facebook.com/v21.0/{pixel_id}/events'
params = {'access_token': access_token}

print(f"Sending Contact test event to Pixel {pixel_id}...")
response = requests.post(url, json=event_data, params=params)

# Check response
result = response.json()
print("\nResponse:", result)

if 'events_received' in result:
    print(f"✅ Success! {result['events_received']} Contact event(s) received")
    print("\nNext steps:")
    print("1. Go to Events Manager")
    print("2. Click on 'course website' pixel")
    print("3. Click 'Test events' tab")
    print(f"4. Enter code: {test_event_code}")
    print("5. You should see a 'Contact' event in the test events")
else:
    print("❌ Error:", result)