#!/usr/bin/env python3
"""
Test script for authentication API endpoints.
"""

import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_auth_endpoints():
    """Test authentication API endpoints."""
    print("Testing Authentication API Endpoints...")
    
    # Test data
    test_user = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    session = requests.Session()
    
    # Test 1: Registration
    print("\n1. Testing user registration...")
    try:
        response = session.post(f"{BASE_URL}/auth/register", json=test_user)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✓ Registration successful")
        else:
            print("✗ Registration failed")
            
    except Exception as e:
        print(f"✗ Registration error: {e}")
    
    # Test 2: Login
    print("\n2. Testing user login...")
    try:
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"],
            "remember": False
        }
        response = session.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Login successful")
        else:
            print("✗ Login failed")
            
    except Exception as e:
        print(f"✗ Login error: {e}")
    
    # Test 3: Check session
    print("\n3. Testing session check...")
    try:
        response = session.get(f"{BASE_URL}/auth/session")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Session check successful")
        else:
            print("✗ Session check failed")
            
    except Exception as e:
        print(f"✗ Session check error: {e}")
    
    # Test 4: Get current user
    print("\n4. Testing get current user...")
    try:
        response = session.get(f"{BASE_URL}/auth/me")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Get current user successful")
        else:
            print("✗ Get current user failed")
            
    except Exception as e:
        print(f"✗ Get current user error: {e}")
    
    # Test 5: Password reset request
    print("\n5. Testing password reset request...")
    try:
        reset_data = {"email": test_user["email"]}
        response = session.post(f"{BASE_URL}/auth/reset-password", json=reset_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Password reset request successful")
        else:
            print("✗ Password reset request failed")
            
    except Exception as e:
        print(f"✗ Password reset request error: {e}")
    
    # Test 6: Change password
    print("\n6. Testing password change...")
    try:
        change_data = {
            "current_password": test_user["password"],
            "new_password": "newpass123"
        }
        response = session.post(f"{BASE_URL}/auth/change-password", json=change_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Password change successful")
        else:
            print("✗ Password change failed")
            
    except Exception as e:
        print(f"✗ Password change error: {e}")
    
    # Test 7: Logout
    print("\n7. Testing logout...")
    try:
        response = session.post(f"{BASE_URL}/auth/logout")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Logout successful")
        else:
            print("✗ Logout failed")
            
    except Exception as e:
        print(f"✗ Logout error: {e}")
    
    # Test 8: Validation tests
    print("\n8. Testing validation...")
    
    # Test invalid email
    try:
        invalid_user = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "testpass123"
        }
        response = session.post(f"{BASE_URL}/auth/register", json=invalid_user)
        print(f"Invalid email test - Status: {response.status_code}")
        if response.status_code == 400:
            print("✓ Invalid email validation working")
        else:
            print("✗ Invalid email validation failed")
    except Exception as e:
        print(f"✗ Invalid email test error: {e}")
    
    # Test weak password
    try:
        weak_pass_user = {
            "name": "Test User",
            "email": "test2@example.com",
            "password": "123"
        }
        response = session.post(f"{BASE_URL}/auth/register", json=weak_pass_user)
        print(f"Weak password test - Status: {response.status_code}")
        if response.status_code == 400:
            print("✓ Weak password validation working")
        else:
            print("✗ Weak password validation failed")
    except Exception as e:
        print(f"✗ Weak password test error: {e}")

if __name__ == "__main__":
    print("Authentication API Test Suite")
    print("=" * 50)
    print("Make sure the Flask app is running on http://localhost:5000")
    print("=" * 50)
    
    try:
        test_auth_endpoints()
        print("\n" + "=" * 50)
        print("Test suite completed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")