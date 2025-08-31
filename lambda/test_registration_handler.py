import json
import os
import sys
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock boto3 before importing the handler
sys.modules['boto3'] = Mock()

# Set environment variable
os.environ['TABLE_NAME'] = 'test_registrations'

# Import the handler file directly
exec(open('registration-handler.py').read(), globals())

def test_pending_registration_gets_overwritten():
    """Test that a pending registration is overwritten with new data while paid registrations are rejected"""
    
    # Mock DynamoDB table
    mock_table = Mock()
    
    # First registration attempt - will find a pending registration
    mock_table.get_item.return_value = {
        'Item': {
            'email': 'test@example.com',
            'course_id': '01_ai_automation_for_non_coders',
            'payment_status': 'pending',
            'name': 'Old Name',
            'registration_id': 'old-id-123'
        }
    }
    
    # Patch the global table variable directly
    globals()['table'] = mock_table
    
    with patch('uuid.uuid4', return_value='new-id-456'):
        
        # Test overwriting pending registration
        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'course_id': '01_ai_automation_for_non_coders',
                'name': 'New Name',
                'referral_source': 'google',
                'dietary_requirements': 'none'
            })
        }
        
        response = lambda_handler(event, {})
        
        # Should succeed and overwrite
        assert response['statusCode'] == 200
        assert 'Registration successful' in json.loads(response['body'])['message']
        
        # Verify put_item was called (overwriting the old data)
        mock_table.put_item.assert_called_once()
        new_item = mock_table.put_item.call_args[1]['Item']
        assert new_item['name'] == 'New Name'
        assert new_item['registration_id'] == 'new-id-456'
        
        # Now test with a paid registration
        mock_table.reset_mock()
        mock_table.get_item.return_value = {
            'Item': {
                'email': 'paid@example.com',
                'course_id': '01_ai_automation_for_non_coders',
                'payment_status': 'paid',
                'name': 'Paid User'
            }
        }
        
        event = {
            'body': json.dumps({
                'email': 'paid@example.com',
                'course_id': '01_ai_automation_for_non_coders',
                'name': 'Trying to Re-register',
                'referral_source': 'google',
                'dietary_requirements': 'none'
            })
        }
        
        response = lambda_handler(event, {})
        
        # Should be rejected
        assert response['statusCode'] == 400
        response_body = json.loads(response['body'])
        assert response_body['error'] == 'email_already_registered'
        assert 'already been registered and paid' in response_body['message']
        
        # Verify put_item was NOT called for paid registration
        mock_table.put_item.assert_not_called()

if __name__ == '__main__':
    test_pending_registration_gets_overwritten()
    print("Test passed!")