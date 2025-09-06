import json
import requests
import pytest
import boto3
from typing import List, Dict, Any


def load_terraform_outputs():
    """Load terraform outputs from JSON file"""
    with open('test/terraform-outputs.json', 'r') as f:
        return json.load(f)


@pytest.fixture(scope="module")
def terraform_outputs():
    """Pytest fixture to load terraform outputs"""
    return load_terraform_outputs()


@pytest.fixture(scope="module")
def livestream_endpoint(terraform_outputs):
    """Pytest fixture to get livestream registration endpoint URL"""
    api_url = terraform_outputs['api_gateway_invoke_url']['value']
    return f"{api_url}/livestream"


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
            print(f"Cleaned up livestream test item: {item}")
        except Exception as e:
            print(f"Failed to clean up livestream item {item}: {e}")
    
    # Clean up any livestream test items that might exist
    try:
        response = table.scan(
            FilterExpression="course_id = :course_id",
            ExpressionAttributeValues={":course_id": "tax-livestream-01"}
        )
        
        for item in response.get('Items', []):
            # Only clean up test emails to avoid deleting real registrations
            if item.get('email', '').startswith('test'):
                try:
                    table.delete_item(
                        Key={
                            'course_id': item['course_id'],
                            'email': item['email']
                        }
                    )
                    print(f"Cleaned up livestream test email: {item['email']}")
                except Exception as e:
                    print(f"Failed to clean up livestream test email: {e}")
                    
    except Exception as e:
        print(f"Failed to scan for livestream test items: {e}")


@pytest.mark.usefixtures("dynamodb_cleanup")
class TestLivestreamRegistration:
    """Test livestream registration endpoint functionality"""
    
    def test_valid_livestream_registration(self, livestream_endpoint, dynamodb_cleanup):
        """Test valid livestream registration submission and verify livestream-specific attributes"""
        test_email = "test_livestream@example.com"
        payload = {
            "name": "Test Livestream User",
            "email": test_email
        }
        
        # Track for cleanup
        dynamodb_cleanup("tax-livestream-01", test_email)
        
        response = requests.post(
            livestream_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert 'registration_id' in data, f"Expected registration_id in response: {data}"
        assert data['message'] == 'Registration successful', f"Unexpected message: {data['message']}"
        
        # Verify the livestream-specific registration was created in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('course_registrations')
        
        db_response = table.get_item(
            Key={
                'course_id': 'tax-livestream-01',
                'email': test_email
            }
        )
        
        assert 'Item' in db_response, "Registration not found in DynamoDB"
        item = db_response['Item']
        
        # Verify livestream-specific attributes
        assert item['course_id'] == 'tax-livestream-01', f"Wrong course_id: {item['course_id']}"
        assert item['payment_status'] == 'paid', f"Expected paid status: {item['payment_status']}"
        assert item['payment_amount'] == 0, f"Expected $0 payment: {item['payment_amount']}"
        assert item['registration_type'] == 'livestream', f"Wrong registration type: {item.get('registration_type')}"
    
    def test_missing_required_fields(self, livestream_endpoint):
        """Test validation for missing name and email fields"""
        # Missing name
        response = requests.post(
            livestream_endpoint,
            json={"email": "test@example.com"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for missing name, got {response.status_code}"
        assert 'name' in response.json()['error'].lower(), "Error should mention name"
        
        # Missing email  
        response = requests.post(
            livestream_endpoint,
            json={"name": "Test User"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for missing email, got {response.status_code}"
        assert 'email' in response.json()['error'].lower(), "Error should mention email"
    
    def test_duplicate_registration_handling(self, livestream_endpoint, dynamodb_cleanup):
        """Test that duplicate email registrations return error"""
        test_email = "test_duplicate@example.com"
        payload = {
            "name": "First Registration",
            "email": test_email
        }
        
        # Track for cleanup
        dynamodb_cleanup("tax-livestream-01", test_email)
        
        # First registration should succeed
        response1 = requests.post(
            livestream_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response1.status_code == 200, f"First registration failed: {response1.status_code}: {response1.text}"
        first_registration_id = response1.json()['registration_id']
        
        # Second registration with same email should return error
        response2 = requests.post(
            livestream_endpoint,
            json={"name": "Second Registration", "email": test_email},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response2.status_code == 409, f"Second registration should fail with 409: {response2.status_code}: {response2.text}"
        data = response2.json()
        assert 'error' in data, f"Expected error in response: {data}"
        assert 'already exists' in data['error'].lower(), f"Expected 'already exists' in error message: {data['error']}"
    
    def test_cors_preflight_request(self, livestream_endpoint):
        """Test CORS preflight request for livestream endpoint"""
        response = requests.options(
            livestream_endpoint,
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200 for OPTIONS, got {response.status_code}"
        
        # Check required CORS headers
        assert 'Access-Control-Allow-Origin' in response.headers, "Missing CORS Allow-Origin header"
        assert 'Access-Control-Allow-Methods' in response.headers, "Missing CORS Allow-Methods header"
        assert 'POST' in response.headers['Access-Control-Allow-Methods'], "POST not in allowed methods"
    
    def test_email_normalization_and_free_registration(self, livestream_endpoint, dynamodb_cleanup):
        """Test email normalization and verify free registration attributes"""
        test_email_upper = "Test.LiveStream@Example.COM"
        test_email_lower = test_email_upper.lower()
        
        payload = {
            "name": "Test Case User",
            "email": test_email_upper
        }
        
        # Track for cleanup using lowercase email
        dynamodb_cleanup("tax-livestream-01", test_email_lower)
        
        response = requests.post(
            livestream_endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        assert response.status_code == 200, f"Registration failed: {response.status_code}: {response.text}"
        
        # Verify email normalization and free registration in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('course_registrations')
        
        db_response = table.get_item(
            Key={
                'course_id': 'tax-livestream-01',
                'email': test_email_lower
            }
        )
        
        assert 'Item' in db_response, "Registration not found with lowercase email"
        item = db_response['Item']
        assert item['email'] == test_email_lower, f"Email not normalized: {item['email']}"
        assert item['payment_amount'] == 0, f"Should be free registration: {item['payment_amount']}"
        assert item['payment_status'] == 'paid', f"Should be auto-paid: {item['payment_status']}"