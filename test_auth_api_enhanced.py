#!/usr/bin/env python3
"""
Enhanced test suite for authentication API endpoints.
Tests all authentication functionality including registration, login, logout,
password reset, social login, and session management.
"""

import sys
import os
import json
import secrets
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.user import User

class TestAuthAPI:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        
    def setup(self):
        """Set up test environment."""
        self.app_context.push()
        db.create_all()
        
    def teardown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def get_csrf_token(self):
        """Get CSRF token for API requests."""
        response = self.client.get('/api/auth/csrf-token')
        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('csrf_token')
        return None
        
    def test_csrf_token_endpoint(self):
        """Test CSRF token generation endpoint."""
        print("Testing CSRF token endpoint...")
        
        response = self.client.get('/api/auth/csrf-token')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'csrf_token' in data
        assert len(data['csrf_token']) > 0
        
        print("✓ CSRF token endpoint works correctly")
        
    def test_user_registration(self):
        """Test user registration API endpoint."""
        print("Testing user registration...")
        
        csrf_token = self.get_csrf_token()
        
        # Test successful registration
        user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'TestPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['name'] == 'Test User'
        assert 'csrf_token' in data
        
        # Test duplicate email registration
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Email already registered' in data['error']
        
        # Test invalid email format
        invalid_user_data = {
            'name': 'Test User 2',
            'email': 'invalid-email',
            'password': 'TestPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(invalid_user_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid email format' in data['error']
        
        # Test weak password
        weak_password_data = {
            'name': 'Test User 3',
            'email': 'test3@example.com',
            'password': '123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/register',
                                  data=json.dumps(weak_password_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Password must be at least 8 characters long' in data['error']
        
        # Test missing CSRF token
        response = self.client.post('/api/auth/register',
                                  data=json.dumps({
                                      'name': 'Test User 4',
                                      'email': 'test4@example.com',
                                      'password': 'TestPassword123'
                                  }),
                                  content_type='application/json')
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'Invalid CSRF token' in data['error']
        
        print("✓ User registration works correctly")
        
    def test_user_login(self):
        """Test user login API endpoint."""
        print("Testing user login...")
        
        csrf_token = self.get_csrf_token()
        
        # Create a test user first
        user = User(
            name='Login Test User',
            email='login@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Test successful login
        login_data = {
            'email': 'login@example.com',
            'password': 'TestPassword123',
            'remember': False,
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert 'user' in data
        assert data['user']['email'] == 'login@example.com'
        assert 'csrf_token' in data
        
        # Test login with remember me
        login_data['remember'] = True
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        
        # Test invalid credentials
        invalid_login_data = {
            'email': 'login@example.com',
            'password': 'WrongPassword',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(invalid_login_data),
                                  content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid email or password' in data['error']
        
        # Test login with unverified email
        unverified_user = User(
            name='Unverified User',
            email='unverified@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=False
        )
        db.session.add(unverified_user)
        db.session.commit()
        
        unverified_login_data = {
            'email': 'unverified@example.com',
            'password': 'TestPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(unverified_login_data),
                                  content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Email not verified' in data['error']
        
        print("✓ User login works correctly")
        
    def test_session_management(self):
        """Test session management endpoints."""
        print("Testing session management...")
        
        csrf_token = self.get_csrf_token()
        
        # Create and login a test user
        user = User(
            name='Session Test User',
            email='session@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        login_data = {
            'email': 'session@example.com',
            'password': 'TestPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        login_response_data = json.loads(response.data)
        csrf_token = login_response_data['csrf_token']
        
        # Test session check when authenticated
        response = self.client.get('/api/auth/session')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] == True
        assert 'user' in data
        assert data['user']['email'] == 'session@example.com'
        
        # Test current user endpoint
        response = self.client.get('/api/auth/me')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == 'session@example.com'
        
        # Test session refresh
        response = self.client.post('/api/auth/refresh-session',
                                  data=json.dumps({'_csrf_token': csrf_token}),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Session refreshed successfully'
        assert 'csrf_token' in data
        
        # Test logout
        response = self.client.post('/api/auth/logout',
                                  data=json.dumps({'_csrf_token': csrf_token}),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Logout successful'
        
        # Test session check when not authenticated
        response = self.client.get('/api/auth/session')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] == False
        
        print("✓ Session management works correctly")
        
    def test_password_reset(self):
        """Test password reset functionality."""
        print("Testing password reset...")
        
        csrf_token = self.get_csrf_token()
        
        # Create a test user
        user = User(
            name='Reset Test User',
            email='reset@example.com',
            password_hash=User.hash_password('OldPassword123'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Test password reset request
        reset_request_data = {
            'email': 'reset@example.com',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/reset-password',
                                  data=json.dumps(reset_request_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'password reset link has been sent' in data['message']
        
        # Test password reset request with non-existent email
        reset_request_data['email'] = 'nonexistent@example.com'
        response = self.client.post('/api/auth/reset-password',
                                  data=json.dumps(reset_request_data),
                                  content_type='application/json')
        
        assert response.status_code == 200  # Should still return success to prevent enumeration
        
        # Test password reset with token
        reset_token = user.get_reset_token()
        
        reset_password_data = {
            'password': 'NewPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post(f'/api/auth/reset-password/{reset_token}',
                                  data=json.dumps(reset_password_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password reset successful'
        
        # Verify password was changed
        updated_user = User.query.get(user.id)
        assert updated_user.check_password('NewPassword123')
        assert not updated_user.check_password('OldPassword123')
        
        # Test password reset with invalid token
        response = self.client.post('/api/auth/reset-password/invalid-token',
                                  data=json.dumps(reset_password_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Invalid or expired token' in data['error']
        
        print("✓ Password reset works correctly")
        
    def test_password_change(self):
        """Test password change for authenticated users."""
        print("Testing password change...")
        
        csrf_token = self.get_csrf_token()
        
        # Create and login a test user
        user = User(
            name='Change Password User',
            email='change@example.com',
            password_hash=User.hash_password('CurrentPassword123'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        login_data = {
            'email': 'change@example.com',
            'password': 'CurrentPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        login_response_data = json.loads(response.data)
        csrf_token = login_response_data['csrf_token']
        
        # Test successful password change
        change_password_data = {
            'current_password': 'CurrentPassword123',
            'new_password': 'NewPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/change-password',
                                  data=json.dumps(change_password_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Password changed successfully'
        
        # Verify password was changed
        updated_user = User.query.get(user.id)
        assert updated_user.check_password('NewPassword123')
        assert not updated_user.check_password('CurrentPassword123')
        
        # Test password change with wrong current password
        wrong_current_data = {
            'current_password': 'WrongPassword',
            'new_password': 'AnotherNewPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/change-password',
                                  data=json.dumps(wrong_current_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Current password is incorrect' in data['error']
        
        # Test password change with same password
        same_password_data = {
            'current_password': 'NewPassword123',
            'new_password': 'NewPassword123',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/change-password',
                                  data=json.dumps(same_password_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'New password must be different' in data['error']
        
        print("✓ Password change works correctly")
        
    def test_social_login(self):
        """Test social login functionality."""
        print("Testing social login...")
        
        csrf_token = self.get_csrf_token()
        
        # Test social login with new user
        social_login_data = {
            'provider': 'google',
            'access_token': 'fake-google-token',
            'user_info': {
                'email': 'social@example.com',
                'name': 'Social User',
                'picture': 'https://example.com/profile.jpg'
            },
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/social-login',
                                  data=json.dumps(social_login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Social login successful'
        assert 'user' in data
        assert data['user']['email'] == 'social@example.com'
        assert data['user']['name'] == 'Social User'
        assert data['is_new_user'] == True
        
        # Test social login with existing user
        response = self.client.post('/api/auth/social-login',
                                  data=json.dumps(social_login_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Social login successful'
        assert data['is_new_user'] == False
        
        # Test social login with unsupported provider
        unsupported_provider_data = {
            'provider': 'twitter',
            'access_token': 'fake-twitter-token',
            'user_info': {
                'email': 'twitter@example.com',
                'name': 'Twitter User'
            },
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/social-login',
                                  data=json.dumps(unsupported_provider_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Unsupported provider' in data['error']
        
        # Test social login with missing user info
        incomplete_data = {
            'provider': 'facebook',
            'access_token': 'fake-facebook-token',
            'user_info': {
                'email': 'incomplete@example.com'
                # Missing name
            },
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/social-login',
                                  data=json.dumps(incomplete_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Email and name are required' in data['error']
        
        print("✓ Social login works correctly")
        
    def run_all_tests(self):
        """Run all authentication API tests."""
        print("=" * 60)
        print("RUNNING AUTHENTICATION API TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_csrf_token_endpoint()
            self.test_user_registration()
            self.test_user_login()
            self.test_session_management()
            self.test_password_reset()
            self.test_password_change()
            self.test_social_login()
            
            print("\n" + "=" * 60)
            print("✅ ALL AUTHENTICATION API TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.teardown()

if __name__ == '__main__':
    tester = TestAuthAPI()
    tester.run_all_tests()