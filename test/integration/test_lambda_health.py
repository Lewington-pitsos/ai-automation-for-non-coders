import json
import requests
import pytest


def load_terraform_outputs():
    """Load terraform outputs from JSON file"""
    with open('test/terraform-outputs.json', 'r') as f:
        return json.load(f)


@pytest.fixture(scope="module")
def terraform_outputs():
    """Pytest fixture to load terraform outputs"""
    return load_terraform_outputs()


class TestLambdaHealth:
    """Test health checks for deployed lambda functions"""
    
    def test_registration_handler_health(self, terraform_outputs):
        """Test registration handler endpoint health"""
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        
        # Test GET request to registration endpoint
        # 403 is expected if GET method not configured or API key required
        response = requests.get(f"{api_url}/register", timeout=30)
        assert response.status_code in [200, 403, 404, 405], f"Unexpected status code: {response.status_code}"
        
        # Test POST request with minimal valid data
        test_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        response = requests.post(f"{api_url}/register", json=test_data, timeout=30)
        assert response.status_code in [200, 201, 400], f"Registration endpoint failed: {response.status_code}"
    
    def test_stripe_webhook_health(self, terraform_outputs):
        """Test stripe webhook endpoint health"""
        webhook_url = terraform_outputs["stripe_webhook_url"]["value"]
        
        # Test that webhook endpoint is accessible
        # Note: We expect this to fail validation but should return 400, not 500
        response = requests.post(webhook_url, json={}, timeout=30)
        assert response.status_code in [200, 400, 401], f"Webhook endpoint error: {response.status_code}"