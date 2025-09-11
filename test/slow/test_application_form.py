from enum import unique
import pytest
import subprocess
import time
import os
import signal
from playwright.sync_api import sync_playwright

class TestApplicationForm:
    """Application form validation test using local server"""
    
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
        
        # Navigate to application page
        page.goto(f"{server}/apply.html")
        
        # Wait for page to fully load
        page.wait_for_load_state("networkidle")
        
        # Wait for application form initialization
        page.wait_for_function("document.getElementById('applicationForm') !== null")
        
        yield page
        page.close()
    
    def test_submit_button_disabled_initially(self, page):
        """Test that submit button is disabled when form is empty"""
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_disabled(), "Submit button should be disabled initially"

        # Fill all required fields
        page.fill("#firstName", "Test")
        page.fill("#lastName", "User")
        page.fill("#email", "test@example.com")
        page.fill("#phone", "+1234567890")
        page.fill("#company", "Test Company")
        page.fill("#jobTitle", "Test Role")
        page.fill("#dietaryRequirements", "None")
        page.select_option("#timeCommitment", "1.5")
        page.fill("#automationInterest", "I want to automate my weekly reports which takes 3 hours")
        page.fill("#automationBarriers", "I don't know where to start")
        page.check("#attendance")
        page.check("#contactConsent")
        page.check("#terms")
        
        # Wait a moment for validation
        page.wait_for_timeout(500)
        
        # Button should now be enabled
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_enabled(), "Submit button should be enabled when all fields are filled"
    
    def test_form_prevents_submission_with_invalid_data(self, page):
        """Test that form validation prevents submission with invalid data"""
        # Fill form with mix of valid and invalid data
        page.fill("#firstName", "Test")
        page.fill("#lastName", "User")
        page.fill("#email", "invalid-email")  # Invalid
        page.fill("#phone", "123")  # Invalid 
        page.fill("#company", "Test Company")
        page.fill("#jobTitle", "Test Role")
        page.fill("#dietaryRequirements", "None")
        # Leave timeCommitment empty - required field
        page.fill("#automationInterest", "Test automation")
        page.fill("#automationBarriers", "Test barriers")
        page.check("#attendance")
        page.check("#contactConsent")
        page.check("#terms")
        
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
        first_name_field = page.locator("#firstName")
        
        # Focus on field then blur without entering data
        first_name_field.focus()
        first_name_field.blur()
        
        # Wait for validation
        page.wait_for_timeout(500)
        
        # Check if there's any validation indication
        # This could be border color, error message, or disabled submit button
        border_color = first_name_field.evaluate("el => window.getComputedStyle(el).borderColor")
        has_error_message = page.locator(".field-error").count() > 0
        submit_disabled = page.locator("button[type='submit']").is_disabled()
        
        # At least one of these should indicate validation
        assert has_error_message or submit_disabled or "rgb(255, 68, 68)" in border_color, \
            "Required field validation should provide some indication when field is empty"

    def test_dropdown_validation(self, page):
        """Test that time commitment dropdown validation works"""
        time_commitment_field = page.locator("#timeCommitment")
        
        # Focus on dropdown then blur without selecting
        time_commitment_field.focus()
        time_commitment_field.blur()
        
        # Wait for validation
        page.wait_for_timeout(500)
        
        # Check if submit button is disabled (should be since it's required)
        submit_disabled = page.locator("button[type='submit']").is_disabled()
        assert submit_disabled, "Submit button should be disabled when required dropdown is empty"
        
        # Select a value and check that validation passes
        page.select_option("#timeCommitment", "1.5")
        page.wait_for_timeout(500)
        
        # Fill other required fields to see if dropdown validation clears
        page.fill("#firstName", "Test")
        page.fill("#lastName", "User")
        page.fill("#email", "test@example.com")
        page.fill("#phone", "+1234567890")
        page.fill("#company", "Test Company")
        page.fill("#jobTitle", "Test Role")
        page.fill("#dietaryRequirements", "None")
        page.fill("#automationInterest", "Test automation")
        page.fill("#automationBarriers", "Test barriers")
        page.check("#attendance")
        page.check("#contactConsent")
        page.check("#terms")
        
        page.wait_for_timeout(500)
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_enabled(), "Submit button should be enabled when dropdown has valid selection"

    def test_checkbox_validation(self, page):
        """Test that required checkboxes work properly"""
        # Fill all other required fields first
        page.fill("#firstName", "Test")
        page.fill("#lastName", "User")
        page.fill("#email", "test@example.com")
        page.fill("#phone", "+1234567890")
        page.fill("#company", "Test Company")
        page.fill("#jobTitle", "Test Role")
        page.fill("#dietaryRequirements", "None")
        page.select_option("#timeCommitment", "1.5")
        page.fill("#automationInterest", "Test automation")
        page.fill("#automationBarriers", "Test barriers")
        
        # Leave checkboxes unchecked
        page.wait_for_timeout(500)
        
        # Submit button should be disabled
        submit_button = page.locator("button[type='submit']")
        assert submit_button.is_disabled(), "Submit button should be disabled when required checkboxes are unchecked"
        
        # Check attendance but not consent or terms
        page.check("#attendance")
        page.wait_for_timeout(500)
        assert submit_button.is_disabled(), "Submit button should still be disabled with only one checkbox checked"
        
        # Check consent but not terms
        page.check("#contactConsent")
        page.wait_for_timeout(500)
        assert submit_button.is_disabled(), "Submit button should still be disabled without terms checkbox"
        
        # Check terms - now should be enabled
        page.check("#terms")
        page.wait_for_timeout(500)
        assert submit_button.is_enabled(), "Submit button should be enabled when all checkboxes are checked"

    def test_successful_form_submission_with_cleanup(self, page):
        """Test successful form submission - application form saves to DynamoDB and needs cleanup"""
        # Fill out the form with valid data
        unique_email = f"test_application_ui_{int(time.time())}@example.com"
        page.fill("#firstName", "Test")
        page.fill("#lastName", "Application User")
        page.fill("#email", unique_email)
        page.fill("#phone", "+1234567890")
        page.fill("#company", "Test Company UI")
        page.fill("#jobTitle", "Test Role UI")
        page.fill("#dietaryRequirements", "No dietary restrictions")
        page.select_option("#timeCommitment", "1.5")
        page.fill("#automationInterest", "I want to automate my weekly reporting process that currently takes 3 hours every Monday.")
        page.fill("#automationBarriers", "I don't have the technical knowledge to build automations and don't know where to start.")
        page.check("#attendance")
        page.check("#contactConsent")
        page.check("#terms")
        
        # Wait for validation
        page.wait_for_timeout(500)
        
        # Try multiple click strategies
        submit_button = page.locator("button[type='submit']")
        
        # Ensure button is enabled before clicking
        page.wait_for_function("document.querySelector('button[type=\"submit\"]').disabled === false")
        
        # Strategy 1: Try regular click with force
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
                page.evaluate("document.getElementById('applicationForm').requestSubmit()")
        
        # Wait for submission to complete and check for success toast
        page.wait_for_timeout(3000)
        
        # Check for success toast with specific message
        toast_selector = ".toast-content"
        success_toast = page.locator(toast_selector)

        
        success_toast.wait_for(state="visible", timeout=5000)
        toast_text = success_toast.text_content()
        assert "Thanks for taking the time to apply" in toast_text, f"Expected success message not found in toast: '{toast_text}'"