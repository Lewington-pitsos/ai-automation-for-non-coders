import json
import requests
import pytest
import boto3
from typing import List, Dict, Any


def load_terraform_outputs():
    """Load terraform outputs from JSON file"""
    with open('test/terraform-outputs.json', 'r') as f:
        return json.load(f)


def load_test_credentials():
    """Load test credentials from terraform.tfvars file"""
    try:
        with open('tf/terraform.tfvars', 'r') as f:
            credentials = {}
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    if key == 'stripe_webhook_secret':
                        credentials[key] = value
            return credentials
    except Exception as e:
        raise Exception(f"Failed to load credentials from tf/terraform.tfvars: {e}")


@pytest.fixture(scope="module")
def terraform_outputs():
    """Pytest fixture to load terraform outputs"""
    return load_terraform_outputs()


@pytest.fixture(scope="module")
def test_credentials():
    """Pytest fixture to load test credentials"""
    return load_test_credentials()


@pytest.fixture(scope="module")
def dynamodb_cleanup():
    """Fixture to track and clean up DynamoDB items created during tests"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('course_registrations')
    
    # Track items to clean up
    items_to_delete = []
    
    def track_item(course_id: str, email: str):
        """Track an item for cleanup"""
        items_to_delete.append({
            'course_id': course_id,
            'email': email.lower()
        })
    
    # Provide the tracking function to tests
    yield track_item
    
    # Cleanup: Delete all tracked items regardless of test outcome
    for item in items_to_delete:
        try:
            table.delete_item(Key=item)
            print(f"Cleaned up DynamoDB item: {item}")
        except Exception as e:
            print(f"Failed to clean up item {item}: {e}")
    
    # Also clean up any test items that might have been created without tracking
    # Search for and delete all items with test course_id
    try:
        response = table.scan(
            FilterExpression="course_id = :course_id",
            ExpressionAttributeValues={":course_id": "test-course"}
        )
        
        for item in response.get('Items', []):
            try:
                table.delete_item(
                    Key={
                        'course_id': item['course_id'],
                        'email': item['email']
                    }
                )
                print(f"Cleaned up test item: course_id={item['course_id']}, email={item['email']}")
            except Exception as e:
                print(f"Failed to clean up test item: {e}")
        
        # Also clean up any items with emails starting with "test"
        response = table.scan()
        for item in response.get('Items', []):
            if item.get('email', '').startswith('test'):
                try:
                    table.delete_item(
                        Key={
                            'course_id': item['course_id'],
                            'email': item['email']
                        }
                    )
                    print(f"Cleaned up test email item: course_id={item['course_id']}, email={item['email']}")
                except Exception as e:
                    print(f"Failed to clean up test email item: {e}")
                    
    except Exception as e:
        print(f"Failed to scan for test items: {e}")


@pytest.mark.usefixtures("dynamodb_cleanup")
class TestLambdaHealth:
    """Test health checks for deployed lambda functions"""
    
    def test_registration_handler_health(self, terraform_outputs, dynamodb_cleanup):
        """Test registration handler endpoint health"""
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        
        # Test GET request to registration endpoint
        # 403 is expected if GET method not configured or API key required
        response = requests.get(f"{api_url}/register", timeout=30)
        assert response.status_code in [200, 403, 404, 405], f"Unexpected status code: {response.status_code}, {response.text}"

        # Test POST request with minimal valid data
        test_email = "test_health@example.com"
        test_data = {
            "email": test_email,
            "name": "Test User",
            "course_id": "test-course",  # Use test course ID for testing
            "referral_source": "test",
            "phone": "+1234567890",
            "dietary_requirements": "none"
        }
        
        # Track item for cleanup
        dynamodb_cleanup("test-course", test_email)
        
        response = requests.post(f"{api_url}/register", json=test_data, timeout=30)
        assert response.status_code in [200, 201, 400], f"Registration endpoint failed: {response.status_code}, {response.text}"

    def test_invalid_course_id_rejected(self, terraform_outputs):
        """Test that invalid course IDs are rejected"""
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        
        # Test with invalid course ID (won't create DB entry, so no cleanup needed)
        test_data = {
            "email": "test_invalid@example.com",
            "name": "Test User",
            "course_id": "invalid-course-id",
            "referral_source": "test",
            "phone": "+1234567890",
            "dietary_requirements": "none"
        }
        response = requests.post(f"{api_url}/register", json=test_data, timeout=30)
        assert response.status_code == 400, f"Expected 400 for invalid course ID: {response.status_code}"
        
        # Check error message
        response_data = response.json()
        assert response_data.get("error") == "invalid_course_id", f"Expected invalid_course_id error: {response_data}"
    
    def test_stripe_webhook_health(self, terraform_outputs, test_credentials):
        """Test stripe webhook endpoint health"""
        webhook_url = terraform_outputs["stripe_webhook_url"]["value"]
        
        # Test that webhook endpoint is accessible
        # Generate a valid Stripe signature for the test payload
        import time
        import hmac
        import hashlib
        
        # Load webhook secret from terraform.tfvars
        webhook_secret = test_credentials.get("stripe_webhook_secret")
        if not webhook_secret:
            raise Exception("No stripe_webhook_secret found in tf/terraform.tfvars")
        
        timestamp = str(int(time.time()))
        # Valid Stripe webhook test payload with client_reference_id
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
                    "client_reference_id": "test-registration-id-123",
                    "customer_details": {"email": "test@example.com"},
                    "amount_total": 5000
                }
            }
        })
        
        # Create the signed payload as Stripe does
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        stripe_signature = f"t={timestamp},v1={signature}"
        
        headers = {
            "stripe-signature": stripe_signature,
            "content-type": "application/json"
        }
        
        # This should now pass signature validation with the real webhook secret
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=30)
        assert response.status_code in [200, 400, 401, 404], f"Webhook endpoint error: {response.status_code}, {response.text}"
    
    def test_end_to_end_registration_and_payment(self, terraform_outputs, test_credentials, dynamodb_cleanup):
        """Test complete flow: registration then payment webhook"""
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        webhook_url = terraform_outputs["stripe_webhook_url"]["value"]
        
        # Step 1: Create a registration
        test_email = "test_e2e@example.com"
        test_data = {
            "email": test_email,
            "name": "E2E Test User",
            "phone": "+1234567890",
            "course_id": "test-course",
            "referral_source": "test",
            "dietary_requirements": "none"
        }
        
        # Track for cleanup
        dynamodb_cleanup("test-course", test_email)
        
        # Register
        response = requests.post(f"{api_url}/register", json=test_data, timeout=30)
        assert response.status_code == 200, f"Registration failed: {response.status_code}, {response.text}"
        
        registration_data = response.json()
        registration_id = registration_data.get("registration_id")
        assert registration_id, "No registration_id returned"
        
        # Step 2: Simulate payment webhook with the registration_id
        import time
        import hmac
        import hashlib
        
        webhook_secret = test_credentials.get("stripe_webhook_secret")
        if not webhook_secret:
            pytest.skip("No stripe_webhook_secret found")
        
        timestamp = str(int(time.time()))
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_e2e",
                    "client_reference_id": registration_id,  # Use actual registration ID
                    "customer_details": {"email": test_email},
                    "amount_total": 61200  # $612 in cents
                }
            }
        })
        
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        stripe_signature = f"t={timestamp},v1={signature}"
        
        headers = {
            "stripe-signature": stripe_signature,
            "content-type": "application/json"
        }
        
        # Process payment
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=30)
        assert response.status_code == 200, f"Payment webhook failed: {response.status_code}, {response.text}"
    
    def test_stripe_webhook_missing_client_reference_id(self, terraform_outputs, test_credentials):
        """Test that webhook properly handles missing client_reference_id"""
        webhook_url = terraform_outputs["stripe_webhook_url"]["value"]
        
        import time
        import hmac
        import hashlib
        
        webhook_secret = test_credentials.get("stripe_webhook_secret")
        if not webhook_secret:
            raise Exception("No stripe_webhook_secret found in tf/terraform.tfvars")
        
        timestamp = str(int(time.time()))
        # Webhook payload WITHOUT client_reference_id
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_456",
                    "customer_details": {"email": "test@example.com"},
                    "amount_total": 5000
                }
            }
        })
        
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        stripe_signature = f"t={timestamp},v1={signature}"
        
        headers = {
            "stripe-signature": stripe_signature,
            "content-type": "application/json"
        }
        
        # This should handle missing client_reference_id gracefully
        response = requests.post(webhook_url, data=payload, headers=headers, timeout=30)
        # Should return 200 (if found by email) or 404 (if not found)
        assert response.status_code in [200, 404], f"Unexpected status for missing client_reference_id: {response.status_code}, {response.text}"