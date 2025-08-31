import json
import requests
import pytest
from pathlib import Path


def load_terraform_outputs():
    """Load terraform outputs from JSON file"""
    with open('test/terraform-outputs.json', 'r') as f:
        return json.load(f)


@pytest.fixture(scope="module")
def terraform_outputs():
    """Pytest fixture to load terraform outputs"""
    return load_terraform_outputs()


@pytest.fixture(scope="module")
def contact_endpoint(terraform_outputs):
    """Pytest fixture to get contact form endpoint URL"""
    api_url = terraform_outputs['api_gateway_invoke_url']['value']
    return f"{api_url}/contact"


class TestContactForm:
    """Test contact form endpoint functionality"""
    
    def test_valid_contact_submission(self, contact_endpoint):
        """Test valid contact form submission"""
        payload = {
            "name": "Test User",
            "email": "testuser@example.com",
            "message": "This is a test message from the integration test suite. Please ignore this message."
        }
        
        response = requests.post(
            contact_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'messageId' in data or 'message' in data, f"Expected messageId or message in response: {data}"
    
    def test_missing_name_field(self, contact_endpoint):
        """Test missing name field validation"""
        payload = {
            "email": "testuser@example.com",
            "message": "Test message"
        }
        
        response = requests.post(
            contact_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for missing name, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"
        assert 'name' in data['error'].lower(), f"Error should mention name: {data['error']}"
    
    def test_missing_email_field(self, contact_endpoint):
        """Test missing email field validation"""
        payload = {
            "name": "Test User",
            "message": "Test message"
        }
        
        response = requests.post(
            contact_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for missing email, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"
        assert 'email' in data['error'].lower(), f"Error should mention email: {data['error']}"
    
    def test_missing_message_field(self, contact_endpoint):
        """Test missing message field validation"""
        payload = {
            "name": "Test User",
            "email": "testuser@example.com"
        }
        
        response = requests.post(
            contact_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for missing message, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"
        assert 'message' in data['error'].lower(), f"Error should mention message: {data['error']}"
    
    def test_empty_request_body(self, contact_endpoint):
        """Test empty request body handling"""
        response = requests.post(
            contact_endpoint,
            data='',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for empty body, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"
    
    def test_invalid_json(self, contact_endpoint):
        """Test invalid JSON handling"""
        response = requests.post(
            contact_endpoint,
            data='{"name": "Test", invalid json}',
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid JSON, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"
    
    def test_cors_preflight(self, contact_endpoint):
        """Test CORS preflight request"""
        response = requests.options(
            contact_endpoint,
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200 for OPTIONS, got {response.status_code}"
        
        # Check CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers, "Missing CORS Allow-Origin header"
        assert 'Access-Control-Allow-Methods' in response.headers, "Missing CORS Allow-Methods header"
        assert 'Access-Control-Allow-Headers' in response.headers, "Missing CORS Allow-Headers header"
    
    def test_whitespace_only_fields(self, contact_endpoint):
        """Test that whitespace-only fields are rejected"""
        payload = {
            "name": "   ",
            "email": "test@example.com",
            "message": "\n\t  \n"
        }
        
        response = requests.post(
            contact_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 400, f"Expected 400 for whitespace-only fields, got {response.status_code}"
        
        data = response.json()
        assert 'error' in data, f"Expected error field in response: {data}"