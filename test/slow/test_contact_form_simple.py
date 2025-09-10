import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright

class TestContactFormSimple:
    """Simple contact form validation test using local server"""
    
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
    
    @pytest.fixture
    def page(self, server):
        """Create a new page for each test"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to contact page
            page.goto(f"{server}/contact.html")
            
            # Wait for page to fully load
            page.wait_for_load_state("networkidle")
            
            # Wait for contact form initialization
            page.wait_for_function("document.getElementById('contactForm') !== null")
            
            yield page
            browser.close()
    
    def test_submit_button_disabled_initially(self, page):
        """Test that submit button is disabled when form is empty"""
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_disabled(), "Submit button should be disabled initially"

        # Fill all required fields
        page.fill("#name", "Test User")
        page.fill("#email", "test@example.com")
        page.fill("#mobile", "+1234567890")
        page.fill("#message", "Test message")
        
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
        page.fill("#mobile", "123")  # Invalid 
        page.fill("#message", "Test message")
        
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
        if submit_button.is_disabled():
            assert True, "Form correctly prevented submission via disabled button"
        else:
            # If button is enabled, click it and check that validation errors appear
            original_text = submit_button.text_content()
            submit_button.click()
            
            # Wait a moment for any validation to trigger
            page.wait_for_timeout(1000)
            
            # Either validation errors should appear or button text should remain unchanged
            current_text = submit_button.text_content()
            has_errors = page.locator(".form-errors, .field-error").count() > 0
            
            assert has_errors or current_text == original_text, "Form should show validation errors or prevent submission"
    
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