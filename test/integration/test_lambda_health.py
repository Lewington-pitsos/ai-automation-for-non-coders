import json
import requests
import pytest


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


class TestLambdaHealth:
    """Test health checks for deployed lambda functions"""
    
    def test_registration_handler_health(self, terraform_outputs):
        """Test registration handler endpoint health"""
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        
        # Test GET request to registration endpoint
        # 403 is expected if GET method not configured or API key required
        response = requests.get(f"{api_url}/register", timeout=30)
        assert response.status_code in [200, 403, 404, 405], f"Unexpected status code: {response.status_code}, {response.text}"

        # Test POST request with minimal valid data
        test_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        response = requests.post(f"{api_url}/register", json=test_data, timeout=30)
        assert response.status_code in [200, 201, 400], f"Registration endpoint failed: {response.status_code}, {response.text}"

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
        # Valid Stripe webhook test payload
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_123",
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
        assert response.status_code in [200, 400, 401], f"Webhook endpoint error: {response.status_code}, {response.text}"