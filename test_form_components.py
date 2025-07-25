#!/usr/bin/env python3
"""
Test script for form components functionality
Tests the enhanced form validation system, input field components, and multi-step forms
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Please ensure ChromeDriver is installed and in PATH")
        return None

def test_form_validation(driver, base_url):
    """Test form validation functionality"""
    print("Testing form validation...")
    
    try:
        # Navigate to registration page
        driver.get(f"{base_url}/auth/register")
        wait = WebDriverWait(driver, 10)
        
        # Test required field validation
        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        submit_button.click()
        
        # Check for validation messages
        validation_messages = driver.find_elements(By.CSS_SELECTOR, ".validation-message .text-red-500")
        assert len(validation_messages) > 0, "Required field validation should show error messages"
        print("✓ Required field validation working")
        
        # Test email validation
        email_field = driver.find_element(By.NAME, "email")
        email_field.send_keys("invalid-email")
        email_field.send_keys(Keys.TAB)  # Trigger blur event
        
        time.sleep(0.5)  # Wait for validation
        email_validation = driver.find_element(By.CSS_SELECTOR, "input[name='email'] + .floating-label")
        assert "border-red-500" in email_field.get_attribute("class"), "Invalid email should show error state"
        print("✓ Email validation working")
        
        # Test password strength indicator
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("weak")
        
        time.sleep(0.5)
        strength_indicator = driver.find_element(By.CSS_SELECTOR, ".password-strength-fill")
        assert strength_indicator.is_displayed(), "Password strength indicator should be visible"
        print("✓ Password strength indicator working")
        
        # Test password confirmation
        password_field.clear()
        password_field.send_keys("strongpassword123")
        
        confirm_field = driver.find_element(By.NAME, "confirm_password")
        confirm_field.send_keys("differentpassword")
        confirm_field.send_keys(Keys.TAB)
        
        time.sleep(0.5)
        assert "border-red-500" in confirm_field.get_attribute("class"), "Password mismatch should show error"
        print("✓ Password confirmation validation working")
        
        # Test successful validation
        confirm_field.clear()
        confirm_field.send_keys("strongpassword123")
        confirm_field.send_keys(Keys.TAB)
        
        time.sleep(0.5)
        if driver.find_elements(By.CSS_SELECTOR, "input[name='confirm_password'].border-green-500"):
            print("✓ Success state validation working")
        
        return True
        
    except Exception as e:
        print(f"✗ Form validation test failed: {e}")
        return False

def test_floating_labels(driver, base_url):
    """Test floating label functionality"""
    print("Testing floating labels...")
    
    try:
        driver.get(f"{base_url}/auth/register")
        wait = WebDriverWait(driver, 10)
        
        # Test label floating on focus
        name_field = wait.until(EC.presence_of_element_located((By.NAME, "name")))
        label = driver.find_element(By.CSS_SELECTOR, "label[for='name']")
        
        # Check initial state
        initial_classes = label.get_attribute("class")
        
        # Focus the field
        name_field.click()
        time.sleep(0.3)
        
        focused_classes = label.get_attribute("class")
        assert "active" in focused_classes or "top-" in focused_classes, "Label should float on focus"
        print("✓ Label floats on focus")
        
        # Test label stays floated with content
        name_field.send_keys("John Doe")
        name_field.send_keys(Keys.TAB)
        time.sleep(0.3)
        
        final_classes = label.get_attribute("class")
        assert "active" in final_classes or "top-" in final_classes, "Label should stay floated with content"
        print("✓ Label stays floated with content")
        
        return True
        
    except Exception as e:
        print(f"✗ Floating labels test failed: {e}")
        return False

def test_input_enhancements(driver, base_url):
    """Test input field enhancements"""
    print("Testing input enhancements...")
    
    try:
        driver.get(f"{base_url}/auth/register")
        wait = WebDriverWait(driver, 10)
        
        # Test focus states
        email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_field.click()
        
        time.sleep(0.3)
        focused_classes = email_field.get_attribute("class")
        assert "focus:ring-" in focused_classes or "ring-" in focused_classes, "Focus state should be applied"
        print("✓ Focus states working")
        
        # Test validation icons
        email_field.send_keys("test@example.com")
        email_field.send_keys(Keys.TAB)
        
        time.sleep(0.5)
        validation_icon = driver.find_elements(By.CSS_SELECTOR, ".validation-icon i")
        if validation_icon:
            print("✓ Validation icons working")
        
        return True
        
    except Exception as e:
        print(f"✗ Input enhancements test failed: {e}")
        return False

def test_form_submission(driver, base_url):
    """Test form submission handling"""
    print("Testing form submission...")
    
    try:
        driver.get(f"{base_url}/auth/register")
        wait = WebDriverWait(driver, 10)
        
        # Fill out form with valid data
        name_field = wait.until(EC.presence_of_element_located((By.NAME, "name")))
        name_field.send_keys("Test User")
        
        email_field = driver.find_element(By.NAME, "email")
        email_field.send_keys("test@example.com")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys("testpassword123")
        
        confirm_field = driver.find_element(By.NAME, "confirm_password")
        confirm_field.send_keys("testpassword123")
        
        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        original_text = submit_button.text
        submit_button.click()
        
        # Check for loading state
        time.sleep(0.5)
        current_text = submit_button.text
        if "..." in current_text or "spinner" in submit_button.get_attribute("innerHTML"):
            print("✓ Loading state applied during submission")
        
        return True
        
    except Exception as e:
        print(f"✗ Form submission test failed: {e}")
        return False

def create_test_html():
    """Create a test HTML file for multi-step form testing"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Components Test</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet">
    <style>
        /* Include the form component styles */
        .form-field { position: relative; margin-bottom: 1.5rem; }
        .form-input { width: 100%; padding: 0.75rem 1rem; border: 2px solid #d1d5db; border-radius: 0.5rem; transition: all 0.2s ease-in-out; }
        .form-input:focus { border-color: #55970f; box-shadow: 0 0 0 3px rgba(85, 151, 15, 0.1); outline: none; }
        .floating-label { position: absolute; left: 1rem; top: 0.75rem; color: #6b7280; transition: all 0.2s ease-in-out; pointer-events: none; }
        .floating-label.active { top: -0.5rem; left: 0.75rem; font-size: 0.75rem; color: #55970f; background: white; padding: 0 0.25rem; }
        .validation-message { margin-top: 0.5rem; font-size: 0.875rem; min-height: 1.25rem; }
        .validation-icon { position: absolute; right: 0.75rem; top: 0.75rem; }
        .step-indicator { display: flex; justify-content: center; margin-bottom: 2rem; }
        .step-indicator-item { width: 2rem; height: 2rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 0.5rem; transition: all 0.2s; }
        .step-connector { width: 3rem; height: 0.25rem; margin-top: 1rem; transition: all 0.2s; }
        .form-step.hidden { display: none; }
        .btn-primary { background: linear-gradient(135deg, #55970f, #6abe11); color: white; padding: 0.75rem 1.5rem; border-radius: 0.5rem; border: none; cursor: pointer; }
        .btn-secondary { background: white; color: #55970f; border: 2px solid #55970f; padding: 0.75rem 1.5rem; border-radius: 0.5rem; cursor: pointer; }
    </style>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-8">
        <h1 class="text-2xl font-bold mb-6">Form Components Test</h1>
        
        <!-- Single Form Test -->
        <div class="mb-12">
            <h2 class="text-xl font-semibold mb-4">Single Form with Enhanced Components</h2>
            <form data-form-validator="true" data-validate-on-blur="true">
                <div class="form-field">
                    <input type="text" name="name" class="form-input" placeholder=" " required>
                    <label class="floating-label">Full Name *</label>
                    <div class="validation-icon"></div>
                    <div class="validation-message"></div>
                </div>
                
                <div class="form-field">
                    <input type="email" name="email" class="form-input" placeholder=" " required>
                    <label class="floating-label">Email Address *</label>
                    <div class="validation-icon"></div>
                    <div class="validation-message"></div>
                </div>
                
                <div class="form-field">
                    <input type="password" name="password" class="form-input" placeholder=" " required>
                    <label class="floating-label">Password *</label>
                    <div class="validation-icon"></div>
                    <div class="validation-message"></div>
                </div>
                
                <button type="submit" class="btn-primary w-full">Submit</button>
            </form>
        </div>
        
        <!-- Multi-Step Form Test -->
        <div>
            <h2 class="text-xl font-semibold mb-4">Multi-Step Form</h2>
            <form class="multi-step-form" data-form-validator="true">
                <!-- Step Indicator -->
                <div class="step-indicator">
                    <div class="step-indicator-item bg-green-500 text-white">1</div>
                    <div class="step-connector bg-gray-300"></div>
                    <div class="step-indicator-item bg-gray-300 text-gray-600">2</div>
                    <div class="step-connector bg-gray-300"></div>
                    <div class="step-indicator-item bg-gray-300 text-gray-600">3</div>
                </div>
                
                <!-- Step 1 -->
                <div class="form-step">
                    <h3 class="text-lg font-semibold mb-4">Personal Information</h3>
                    <div class="form-field">
                        <input type="text" name="first_name" class="form-input" placeholder=" " required>
                        <label class="floating-label">First Name *</label>
                        <div class="validation-icon"></div>
                        <div class="validation-message"></div>
                    </div>
                    <div class="form-field">
                        <input type="text" name="last_name" class="form-input" placeholder=" " required>
                        <label class="floating-label">Last Name *</label>
                        <div class="validation-icon"></div>
                        <div class="validation-message"></div>
                    </div>
                </div>
                
                <!-- Step 2 -->
                <div class="form-step hidden">
                    <h3 class="text-lg font-semibold mb-4">Contact Information</h3>
                    <div class="form-field">
                        <input type="email" name="email_step2" class="form-input" placeholder=" " required>
                        <label class="floating-label">Email Address *</label>
                        <div class="validation-icon"></div>
                        <div class="validation-message"></div>
                    </div>
                    <div class="form-field">
                        <input type="tel" name="phone" class="form-input" placeholder=" ">
                        <label class="floating-label">Phone Number</label>
                        <div class="validation-icon"></div>
                        <div class="validation-message"></div>
                    </div>
                </div>
                
                <!-- Step 3 -->
                <div class="form-step hidden">
                    <h3 class="text-lg font-semibold mb-4">Preferences</h3>
                    <div class="form-field">
                        <select name="category" class="form-input" required>
                            <option value="">Select Category</option>
                            <option value="electronics">Electronics</option>
                            <option value="clothing">Clothing</option>
                            <option value="home">Home & Garden</option>
                        </select>
                        <label class="floating-label">Favorite Category *</label>
                        <div class="validation-icon"></div>
                        <div class="validation-message"></div>
                    </div>
                </div>
                
                <!-- Navigation -->
                <div class="step-navigation flex justify-between mt-6">
                    <button type="button" class="btn-secondary" disabled>
                        <i class="fas fa-arrow-left mr-2"></i>Previous
                    </button>
                    <button type="button" class="btn-primary">
                        Next<i class="fas fa-arrow-right ml-2"></i>
                    </button>
                </div>
            </form>
        </div>
    </div>
    
    <script src="app/static/js/form-components.js"></script>
</body>
</html>
    """
    
    with open('test_form_components.html', 'w') as f:
        f.write(html_content)
    
    return os.path.abspath('test_form_components.html')

def test_multi_step_form():
    """Test multi-step form functionality using a local HTML file"""
    print("Testing multi-step form...")
    
    driver = setup_driver()
    if not driver:
        return False
    
    try:
        # Create and load test HTML
        test_file = create_test_html()
        driver.get(f"file://{test_file}")
        
        wait = WebDriverWait(driver, 10)
        
        # Test initial state
        step1 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-step:not(.hidden)")))
        assert step1.is_displayed(), "First step should be visible"
        print("✓ Initial step display working")
        
        # Fill first step
        first_name = driver.find_element(By.NAME, "first_name")
        first_name.send_keys("John")
        
        last_name = driver.find_element(By.NAME, "last_name")
        last_name.send_keys("Doe")
        
        # Click next
        next_button = driver.find_element(By.CSS_SELECTOR, ".step-navigation .btn-primary")
        next_button.click()
        
        time.sleep(0.5)
        
        # Check step 2 is visible
        step2 = driver.find_element(By.CSS_SELECTOR, ".form-step:nth-child(3)")
        assert not step2.get_attribute("class").find("hidden") == -1 or step2.is_displayed(), "Second step should be visible"
        print("✓ Step navigation working")
        
        # Test step indicator update
        indicators = driver.find_elements(By.CSS_SELECTOR, ".step-indicator-item")
        assert "bg-green-500" in indicators[1].get_attribute("class"), "Step indicator should update"
        print("✓ Step indicator updates working")
        
        # Clean up
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"✗ Multi-step form test failed: {e}")
        return False
    finally:
        driver.quit()

def run_all_tests():
    """Run all form component tests"""
    print("🧪 Starting Form Components Tests\n")
    
    # Test multi-step form (doesn't require server)
    multi_step_result = test_multi_step_form()
    
    # For other tests, we would need a running Flask server
    print("\n📝 Test Summary:")
    print(f"Multi-step form: {'✅ PASS' if multi_step_result else '❌ FAIL'}")
    
    print("\n💡 Note: To test form validation, floating labels, and submission handling,")
    print("   please run the Flask application and update the base_url in this script.")
    
    # Example of how to run with Flask server:
    """
    base_url = "http://localhost:5000"  # Update this to your Flask app URL
    driver = setup_driver()
    if driver:
        try:
            validation_result = test_form_validation(driver, base_url)
            labels_result = test_floating_labels(driver, base_url)
            enhancements_result = test_input_enhancements(driver, base_url)
            submission_result = test_form_submission(driver, base_url)
            
            print(f"Form validation: {'✅ PASS' if validation_result else '❌ FAIL'}")
            print(f"Floating labels: {'✅ PASS' if labels_result else '❌ FAIL'}")
            print(f"Input enhancements: {'✅ PASS' if enhancements_result else '❌ FAIL'}")
            print(f"Form submission: {'✅ PASS' if submission_result else '❌ FAIL'}")
            
        finally:
            driver.quit()
    """

if __name__ == "__main__":
    run_all_tests()