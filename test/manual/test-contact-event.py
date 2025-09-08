import requests
import time
import uuid
import hashlib
import random
import sys

# CORRECT PIXEL ID
pixel_id = '1232612085335834'  # Your course website pixel
access_token = 'EAASwaXmwgBsBPTeZCrEXniBubi0Fu0nBfOu4rrEB1l2aDsEw6qbVwZBURWkpUQJds3ZAZBCaxP3ZAf3Eh9c9ZB4cWmUA0saofs0PIHxKGGIKZAiMUzkytpbsC5zg4eoF9EC4vjgkQGptNWKzWguIUu3dCPvdIX37eTRjbEB2PEQS7H4QwjlPQvUwPTk5ncZB7ZCt1aAZDZD'

# Check for --prod flag
is_production = '--prod' in sys.argv
test_event_code = 'TEST62526' if not is_production else None

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

# Hash the random email and phone (following meta_conversions_api.py pattern)
hashed_email = hashlib.sha256(random_email.lower().encode()).hexdigest()
hashed_phone = hashlib.sha256(random_phone.lower().encode()).hexdigest()

# Prepare Contact event for WEBSITE pixel (matching production format)
event_data = {
    'data': [{
        'event_name': 'Contact',
        'event_time': current_time,
        'action_source': 'website',
        'user_data': {
            'client_user_agent': random_user_agent,
            'em': [hashed_email],
            'ph': [hashed_phone]
        },
        'event_source_url': f'https://your-website.com/contact?test={unique_id}',
        'event_id': f'contact_{unique_id}_{current_time}',
        'custom_data': {
            'contact_method': 'contact_form',
            'message_length': 150
        }
    }],
    'access_token': access_token
}

# Add test_event_code only for test events
if not is_production:
    event_data['test_event_code'] = test_event_code

# Send the request
url = f'https://graph.facebook.com/v21.0/{pixel_id}/events'
params = {}  # No params needed when access_token is in payload

event_type = "production" if is_production else "test"
print(f"Sending Contact {event_type} event to Pixel {pixel_id}...")
print(f"Using Email: {random_email}, Phone: {random_phone}, UA: {random_user_agent[:50]}...")
response = requests.post(url, json=event_data)

# Check response
result = response.json()
print("\nResponse:", result)

if 'events_received' in result:
    print(f"✅ Success! {result['events_received']} Contact event(s) received")
    if is_production:
        print("\n🚀 Production event sent! Check Events Manager > course website pixel > Events tab")
    else:
        print("\nNext steps:")
        print("1. Go to Events Manager")
        print("2. Click on 'course website' pixel")
        print("3. Click 'Test events' tab")
        print(f"4. Enter code: {test_event_code}")
        print("5. You should see a 'Contact' event in the test events")
else:
    print("❌ Error:", result)