import pytest
import subprocess
import time
import os
import json
import boto3
from playwright.sync_api import sync_playwright

class TestReferralTracking:
    """Test referral tracking functionality on book-meeting page"""
    
    TEST_REFERRAL_CODE = "test_referral_code"
    
    @pytest.fixture(scope="class")
    def terraform_outputs(self):
        """Load Terraform outputs for API and DynamoDB configuration"""
        outputs_file = os.path.join(os.path.dirname(__file__), "..", "terraform-outputs.json")
        with open(outputs_file, 'r') as f:
            return json.load(f)
    
    @pytest.fixture(scope="class")
    def dynamodb_client(self, terraform_outputs):
        """Create DynamoDB client and get table name"""
        client = boto3.client('dynamodb', region_name='ap-southeast-2')
        return client
    
    @pytest.fixture(scope="class")
    def server(self):
        """Start a local HTTP server"""
        # Change to src directory and start server
        src_path = os.path.abspath("src")
        server_process = subprocess.Popen(
            ["python", "-m", "http.server", "8080"],
            cwd=src_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        time.sleep(1)
        
        yield "http://localhost:8080"
        
        # Cleanup
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    
    @pytest.fixture(scope="class")
    def browser(self):
        """Create a single browser instance for the test"""
        with sync_playwright() as p:
            headless = os.getenv('HEADLESS', 'true').lower() != 'false'
            browser = p.chromium.launch(headless=headless)
            yield browser
            browser.close()
    
    @pytest.fixture
    def page(self, server, browser, terraform_outputs):
        """Create page with API configuration injected"""
        page = browser.new_page()
        
        # Navigate to book-meeting page with referral parameter
        page.goto(f"{server}/book-meeting.html?referral={self.TEST_REFERRAL_CODE}")
        
        # Inject API configuration before other scripts load
        api_url = terraform_outputs["api_gateway_invoke_url"]["value"]
        page.add_init_script(f"""
            window.API_CONFIG = {{
                API_URL: '{api_url}'
            }};
        """)
        
        # Wait for page to fully load
        page.wait_for_load_state("networkidle")
        
        # Wait for components and referral tracking to initialize
        page.wait_for_function("document.querySelector('.calendar-button') !== null")
        page.wait_for_timeout(1000)  # Give time for referral tracking script to initialize
        
        yield page
        page.close()
    
    def cleanup_test_referral_events(self, dynamodb_client):
        """Clean up any existing test referral events before and after test"""
        try:
            # Query for any existing test referral events
            response = dynamodb_client.query(
                TableName='referral_events',
                IndexName='referral-code-index',
                KeyConditionExpression='referral_code = :code',
                ExpressionAttributeValues={
                    ':code': {'S': self.TEST_REFERRAL_CODE}
                }
            )
            
            # Delete any existing items
            for item in response.get('Items', []):
                dynamodb_client.delete_item(
                    TableName='referral_events',
                    Key={'event_id': item['event_id']}
                )
                print(f"Cleaned up existing test referral event: {item['event_id']['S']}")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def test_referral_tracking_and_redirect(self, page, dynamodb_client):
        """Test that clicking book now button tracks referral and redirects to Google Calendar"""
        # Clean up any existing test data
        self.cleanup_test_referral_events(dynamodb_client)
        
        # Verify no existing referral events with our test code
        response = dynamodb_client.query(
            TableName='referral_events',
            IndexName='referral-code-index',
            KeyConditionExpression='referral_code = :code',
            ExpressionAttributeValues={
                ':code': {'S': self.TEST_REFERRAL_CODE}
            }
        )
        initial_count = len(response.get('Items', []))
        assert initial_count == 0, f"Expected 0 initial referral events but found {initial_count}"
        
        # Find the book now button
        book_button = page.locator('.calendar-button')
        assert book_button.is_visible(), "Book now button should be visible"
        
        # Set up a listener for new pages/tabs (Google Calendar redirect) with a context manager
        with page.context.expect_event('page') as new_page_info:
            # Click the book now button
            book_button.click()
        
        # Wait for the new page to open (Google Calendar)
        new_page = new_page_info.value
        new_page_url = new_page.url
        
        # Verify redirect to Google Calendar
        assert 'calendar.google.com' in new_page_url or 'calendar.app.google' in new_page_url, \
            f"Expected redirect to Google Calendar but got: {new_page_url}"
        
        # Close the new page
        new_page.close()
        
        # Wait a moment for the referral event to be processed
        time.sleep(3)
        
        # Check DynamoDB for the new referral event
        response = dynamodb_client.query(
            TableName='referral_events',
            IndexName='referral-code-index',
            KeyConditionExpression='referral_code = :code',
            ExpressionAttributeValues={
                ':code': {'S': self.TEST_REFERRAL_CODE}
            }
        )
        
        final_count = len(response.get('Items', []))
        assert final_count == 1, f"Expected exactly 1 referral event but found {final_count}"
        
        # Verify the referral event details
        event = response['Items'][0]
        assert event['referral_code']['S'] == self.TEST_REFERRAL_CODE
        assert event['event_name']['S'] == 'booking_clicked'
        assert 'timestamp' in event
        assert 'event_id' in event
        
        print(f"Successfully recorded referral event: {event['event_id']['S']}")
        
        # Clean up the test data
        dynamodb_client.delete_item(
            TableName='referral_events',
            Key={'event_id': event['event_id']}
        )
        
        print(f"Cleaned up test referral event: {event['event_id']['S']}")
        
        # Verify cleanup was successful
        final_response = dynamodb_client.query(
            TableName='referral_events',
            IndexName='referral-code-index',
            KeyConditionExpression='referral_code = :code',
            ExpressionAttributeValues={
                ':code': {'S': self.TEST_REFERRAL_CODE}
            }
        )
        
        cleanup_count = len(final_response.get('Items', []))
        assert cleanup_count == 0, f"Cleanup failed - still found {cleanup_count} referral events"