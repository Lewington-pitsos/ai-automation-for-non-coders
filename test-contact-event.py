import requests
import time
import uuid
import hashlib
import random

# CORRECT PIXEL ID
pixel_id = '1232612085335834'  # Your course website pixel
access_token = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

test_event_code = 'TEST62526'

# Generate unique event data each time
current_time = int(time.time())
unique_id = str(uuid.uuid4())

# Generate dynamic user data to prevent deduplication
random_ip = f"{random.randint(192, 203)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101"
]
random_user_agent = random.choice(user_agents)

# Generate random test email and phone for hashing
random_email = f"test{random.randint(1000, 9999)}@gmail.com"
random_phone = f"+61491158824"

# Hash the random email and phone
hashed_email = hashlib.sha256(random_email.encode()).hexdigest()
hashed_phone = hashlib.sha256(random_phone.encode()).hexdigest()

# Prepare test Contact event for WEBSITE pixel
event_data = {
    'data': [{
        'event_name': 'Contact',
        'event_time': current_time,
        'action_source': 'website',
        'user_data': {
            'client_ip_address': random_ip,
            'client_user_agent': random_user_agent,
            'em': [hashed_email],
            'ph': [hashed_phone]
        },
        'event_source_url': f'https://your-website.com/contact?test={unique_id}',
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
print(f"Using IP: {random_ip}, Email: {random_email}, Phone: {random_phone}")
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