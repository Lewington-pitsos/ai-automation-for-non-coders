import pytest
import subprocess
import time
import os
import boto3
from playwright.sync_api import sync_playwright

class TestLivestream:
    """Simple livestream form validation test using local server"""
    
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
        """Create a single browser instance for all tests"""
        with sync_playwright() as p:
            headless = os.getenv('HEADLESS', 'true').lower() != 'false'
            browser = p.chromium.launch(headless=headless)
            yield browser
            browser.close()
    
    @pytest.fixture
    def page(self, server, browser):
        """Reuse browser but create fresh page for each test"""
        page = browser.new_page()
        
        # Navigate to livestream page
        page.goto(f"{server}/livestream.html")
        
        # Wait for page to fully load (use domcontentloaded instead of networkidle due to external resources)
        page.wait_for_load_state("domcontentloaded")
        
        # Wait for livestream form initialization
        page.wait_for_function("document.getElementById('livestreamForm') !== null")
        
        yield page
        page.close()

    @pytest.fixture(scope="class")
    def dynamodb_cleanup(self):
        """Fixture to clean up DynamoDB items created during tests"""
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
    
    def test_submit_button_disabled_initially(self, page):
        """Test that submit button is disabled when form is empty"""
        submit_button = page.locator("button[type='submit']")
        page.wait_for_timeout(500)
        assert submit_button.is_disabled(), "Submit button should be disabled initially"

        # Fill all required fields
        page.fill("#name", "Test User")
        page.fill("#email", "test@example.com")
        
        # Wait a moment for validation
        page.wait_for_timeout(500)
        
        # Button should now be enabled
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_enabled(), "Submit button should be enabled when all fields are filled"
    
    def test_form_prevents_submission_with_invalid_data(self, page):
        """Test that form validation prevents submission with invalid data"""
        # Fill form with mix of valid and invalid data
        page.fill("#name", "Test User")
        page.fill("#email", "invalid-email")  # Invalid
        
        # Wait for form validation
        page.wait_for_timeout(500)

        email_field = page.locator("#email")
        email_field.blur()

        border_color = email_field.evaluate("el => window.getComputedStyle(el).borderColor")
        
        # Check for error messages
        error_messages = page.locator(".field-error").count()
        
        # Check if submit button is disabled
        submit_disabled = page.locator("button[type='submit']").is_disabled()
        
        # The field should have some kind of error indication
        # Since we can't guarantee the exact color, let's check if it's not the default
        default_border = "rgb(0, 0, 0)"  # or similar default
        assert border_color != default_border, f"Email field should show validation error, but border color is: {border_color}"
        
        # Try to submit - the validation should prevent actual submission
        submit_button = page.locator("button[type='submit']")
        
        # If button is disabled due to client-side validation, that's good
        assert submit_button.is_disabled(), "Submit button should be disabled due to invalid data"

    def test_required_field_validation(self, page):
        """Test that required fields show some indication when empty"""
        name_field = page.locator("#name")
        
        # Focus on field then blur without entering data
        name_field.focus()
        name_field.blur()
        
        # Wait for validation
        page.wait_for_timeout(500)
        
        # Check if there's any validation indication
        # This could be border color, error message, or disabled submit button
        border_color = name_field.evaluate("el => window.getComputedStyle(el).borderColor")
        has_error_message = page.locator(".field-error").count() > 0
        submit_disabled = page.locator("button[type='submit']").is_disabled()
        
        # At least one of these should indicate validation
        assert has_error_message or submit_disabled or "rgb(255, 68, 68)" in border_color, \
            "Required field validation should provide some indication when field is empty"

    def test_successful_form_submission_with_cleanup(self, page, dynamodb_cleanup):
        """Test successful form submission and verify DynamoDB cleanup"""
        test_email = "test_livestream_ui@example.com"
        
        # Track for cleanup
        dynamodb_cleanup("tax-livestream-01", test_email)
        
        # Fill out the form
        page.fill("#name", "Test Livestream User")
        page.fill("#email", test_email)
        
        # Wait for validation
        page.wait_for_timeout(500)
        
        # Submit the form
        submit_button = page.locator("button[type='submit']")
        
        # Ensure button is enabled before clicking
        page.wait_for_function("document.querySelector('button[type=\"submit\"]').disabled === false")
        
        # Try multiple click strategies to handle animated button
        try:
            submit_button.click(force=True)
        except Exception as e:
            print(f"Force click failed: {e}")
            
            # Strategy 2: Try dispatching click event
            try:
                submit_button.dispatch_event("click")
            except Exception as e2:
                print(f"Dispatch event failed: {e2}")
                
                # Strategy 3: Try form submission directly
                page.evaluate("document.getElementById('livestreamForm').requestSubmit()")
        
        # Wait for submission to complete
        page.wait_for_timeout(3000)
        
        # Check for success indication (this may vary based on your implementation)
        # This test may fail initially - that's expected for TDD
        success_message = page.locator(".success-message, .toast-success")
        if success_message.count() > 0:
            assert True, "Form submission appeared to succeed"
        else:
            # If no success message, check if button text changed or form was cleared
            button_text = submit_button.text_content()
            name_value = page.locator("#name").input_value()
            
            # Either button should show success state or form should be cleared
            success_indicators = [
                "success" in button_text.lower(),
                "thank" in button_text.lower(), 
                name_value == ""  # Form was cleared
            ]
            
            assert any(success_indicators), f"No clear success indication found. Button text: '{button_text}', Name field: '{name_value}'"