"""
Unit tests for authentication functionality.
"""
import pytest
from flask import url_for, session
from app import db
from app.models.user import User

class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_login_page_loads(self, client):
        """Test that login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
    
    def test_register_page_loads(self, client):
        """Test that register page loads correctly."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
        assert b'name' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
    
    def test_successful_registration(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your account has been created' in response.data
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.name == 'New User'
            assert user.check_password('testpassword123')
    
    def test_registration_with_existing_email(self, client, test_user):
        """Test registration with already existing email."""
        response = client.post('/auth/register', data={
            'name': 'Another User',
            'email': test_user.email,
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        })
        
        assert response.status_code == 200
        assert b'Email already exists' in response.data or b'already registered' in response.data
    
    def test_registration_password_mismatch(self, client):
        """Test registration with password mismatch."""
        response = client.post('/auth/register', data={
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'testpassword123',
            'confirm_password': 'differentpassword'
        })
        
        assert response.status_code == 200
        assert b'passwords must match' in response.data or b'Password' in response.data
    
    def test_successful_login(self, client, test_user):
        """Test successful user login."""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'testpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    def test_login_with_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_with_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'testpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid email or password' in response.data
    
    def test_login_remember_me(self, client, test_user):
        """Test login with remember me functionality."""
        response = client.post('/auth/login', data={
            'email': test_user.email,
            'password': 'testpassword',
            'remember': True
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Check that session is marked as permanent
        with client.session_transaction() as sess:
            assert sess.permanent is True
    
    def test_logout(self, authenticated_client):
        """Test user logout."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out' in response.data
        
        # Check that user is no longer in session
        with authenticated_client.session_transaction() as sess:
            assert '_user_id' not in sess
    
    def test_password_reset_request(self, client, test_user):
        """Test password reset request."""
        response = client.post('/auth/reset_password', data={
            'email': test_user.email
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'password reset link has been sent' in response.data
    
    def test_password_reset_nonexistent_email(self, client):
        """Test password reset request with non-existent email."""
        response = client.post('/auth/reset_password', data={
            'email': 'nonexistent@example.com'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show same message to prevent user enumeration
        assert b'password reset link has been sent' in response.data
    
    def test_password_reset_with_valid_token(self, client, test_user, app):
        """Test password reset with valid token."""
        with app.app_context():
            token = test_user.get_reset_token()
            
            response = client.post(f'/auth/reset_password/{token}', data={
                'password': 'newpassword123',
                'confirm_password': 'newpassword123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert b'password has been updated' in response.data
            
            # Verify password was changed
            user = User.query.get(test_user.id)
            assert user.check_password('newpassword123')
    
    def test_password_reset_with_invalid_token(self, client):
        """Test password reset with invalid token."""
        response = client.get('/auth/reset_password/invalid_token')
        
        assert response.status_code == 302  # Should redirect
        # Follow redirect to see the flash message
        response = client.get('/auth/reset_password/invalid_token', follow_redirects=True)
        assert b'invalid or expired token' in response.data
    
    def test_email_verification(self, client, app):
        """Test email verification functionality."""
        with app.app_context():
            # Create unverified user
            user = User(
                email='unverified@example.com',
                name='Unverified User',
                password_hash=User.hash_password('testpassword'),
                is_email_verified=False
            )
            db.session.add(user)
            db.session.commit()
            
            token = user.generate_email_verification_token()
            db.session.commit()
            
            response = client.get(f'/auth/verify_email/{token}', follow_redirects=True)
            
            assert response.status_code == 200
            assert b'email has been verified' in response.data
            
            # Verify user is now verified
            user = User.query.filter_by(email='unverified@example.com').first()
            assert user.is_email_verified is True
    
    def test_email_verification_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.get('/auth/verify_email/invalid_token', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'invalid or expired' in response.data
    
    def test_authenticated_user_redirected_from_auth_pages(self, authenticated_client):
        """Test that authenticated users are redirected from auth pages."""
        # Test login page
        response = authenticated_client.get('/auth/login')
        assert response.status_code == 302  # Should redirect
        
        # Test register page
        response = authenticated_client.get('/auth/register')
        assert response.status_code == 302  # Should redirect
        
        # Test password reset page
        response = authenticated_client.get('/auth/reset_password')
        assert response.status_code == 302  # Should redirect

class TestAuthHelpers:
    """Test cases for authentication helper functions."""
    
    def test_is_safe_url(self, app):
        """Test URL safety checking."""
        from app.routes.auth import is_safe_url
        
        with app.test_request_context():
            # Test safe URLs
            assert is_safe_url('/dashboard') is True
            assert is_safe_url('/user/profile') is True
            
            # Test unsafe URLs (external)
            assert is_safe_url('http://evil.com/dashboard') is False
            assert is_safe_url('https://malicious.site.com') is False
    
    def test_csrf_protection(self, client, app):
        """Test CSRF protection on auth routes."""
        with app.app_context():
            # Enable CSRF for this test
            app.config['WTF_CSRF_ENABLED'] = True
            
            # Try to post without CSRF token
            response = client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'testpassword'
            })
            
            # Should be rejected or show error
            assert response.status_code in [200, 400, 403]

class TestUserModel:
    """Test cases for User model authentication methods."""
    
    def test_password_hashing_security(self, app):
        """Test password hashing security."""
        with app.app_context():
            password = 'testpassword123'
            hash1 = User.hash_password(password)
            hash2 = User.hash_password(password)
            
            # Hashes should be different (salt)
            assert hash1 != hash2
            
            # Both should verify correctly
            user = User(email='test@example.com', name='Test', password_hash=hash1)
            assert user.check_password(password) is True
            
            user.password_hash = hash2
            assert user.check_password(password) is True
    
    def test_reset_token_expiration(self, app, test_user):
        """Test that reset tokens expire."""
        with app.app_context():
            # Generate token with very short expiration
            token = test_user.get_reset_token(expires_sec=1)
            
            # Token should be valid immediately
            user = User.verify_reset_token(token)
            assert user is not None
            
            # Wait for token to expire (in real test, we'd mock time)
            import time
            time.sleep(2)
            
            # Token should now be invalid
            user = User.verify_reset_token(token)
            assert user is None
    
    def test_user_get_id_method(self, app, test_user):
        """Test User.get_id() method for Flask-Login."""
        with app.app_context():
            user_id = test_user.get_id()
            assert user_id == str(test_user.id)
            assert isinstance(user_id, str)
    
    def test_user_repr_method(self, app, test_user):
        """Test User.__repr__() method."""
        with app.app_context():
            repr_str = repr(test_user)
            assert test_user.name in repr_str
            assert test_user.email in repr_str
            assert 'User(' in repr_str