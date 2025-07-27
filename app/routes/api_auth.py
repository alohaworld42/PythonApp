from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
import secrets
import re
import hmac
from app import db
from app.models.user import User

api_auth_bp = Blueprint('api_auth', __name__)

# CSRF Protection for API endpoints
def verify_csrf_token():
    """Verify CSRF token for state-changing operations."""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.get('_csrf_token')
        request_token = request.headers.get('X-CSRF-Token') or request.json.get('_csrf_token') if request.json else None
        
        if not token or not request_token or not hmac.compare_digest(token, request_token):
            return False
    return True

# Helper functions for authentication
def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

# Authentication endpoints
@api_auth_bp.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for user registration."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=email,
            name=name,
            password_hash=User.hash_password(password),
            is_email_verified=True  # Auto-verify for now
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate CSRF token for the session
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@api_auth_bp.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for user login."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            # Add small delay to prevent timing attacks
            import time
            time.sleep(0.5)
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        if not user.is_email_verified:
            return jsonify({'error': 'Email not verified. Please check your email for verification link.'}), 401
        
        # Set session duration based on remember option
        if remember:
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
        
        # Log user in
        login_user(user, remember=remember)
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate CSRF token
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_image': user.profile_image,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@api_auth_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """API endpoint for user logout."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        logout_user()
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@api_auth_bp.route('/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """API endpoint to get current authenticated user."""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'created_at': current_user.created_at.isoformat(),
                'is_email_verified': current_user.is_email_verified
            }
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get user info'}), 500

@api_auth_bp.route('/auth/reset-password', methods=['POST'])
def request_password_reset():
    """API endpoint to request password reset."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = user.get_reset_token()
            # In a real implementation, you would send an email here
            # For now, we'll log the token for testing purposes
            current_app.logger.info(f"Password reset token for {email}: {reset_token}")
        
        # Always return success to prevent user enumeration
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'error': 'Password reset request failed'}), 500

@api_auth_bp.route('/auth/reset-password/<token>', methods=['POST'])
def reset_password_with_token(token):
    """API endpoint to reset password with token."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verify token and get user
        user = User.verify_reset_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 400
        
        # Update password
        user.password_hash = User.hash_password(password)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@api_auth_bp.route('/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """API endpoint to change password for authenticated user."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if new password is different from current
        if current_user.check_password(new_password):
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        # Update password
        current_user.password_hash = User.hash_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500

@api_auth_bp.route('/auth/social-login', methods=['POST'])
def social_login():
    """API endpoint for social login with OAuth providers."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        provider = data.get('provider')  # 'google', 'facebook', 'amazon'
        access_token = data.get('access_token')
        user_info = data.get('user_info', {})
        
        if not provider or not access_token:
            return jsonify({'error': 'Provider and access token are required'}), 400
        
        if provider not in ['google', 'facebook', 'amazon']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        # Extract user information from the social provider
        email = user_info.get('email', '').strip().lower()
        name = user_info.get('name', '').strip()
        profile_image = user_info.get('picture') or user_info.get('profile_image')
        
        if not email or not name:
            return jsonify({'error': 'Email and name are required from social provider'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format from social provider'}), 400
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # User exists, log them in
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Update profile information if needed
            if user.name != name:
                user.name = name
            if profile_image and user.profile_image == 'default.jpg':
                user.profile_image = profile_image
            
            user.last_login = datetime.utcnow()
            user.is_email_verified = True  # Social accounts are pre-verified
            db.session.commit()
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                password_hash=User.hash_password(secrets.token_urlsafe(32)),  # Random password
                profile_image=profile_image or 'default.jpg',
                is_email_verified=True,  # Social accounts are pre-verified
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
        
        # Log user in
        login_user(user, remember=True)  # Remember social logins
        
        # Generate CSRF token
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Social login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_image': user.profile_image,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token'],
            'is_new_user': user.created_at > datetime.utcnow() - timedelta(minutes=1)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Social login error: {str(e)}")
        return jsonify({'error': 'Social login failed'}), 500

@api_auth_bp.route('/auth/session', methods=['GET'])
def check_session():
    """API endpoint to check session status."""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'name': current_user.name,
                    'profile_image': current_user.profile_image,
                    'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                    'is_email_verified': current_user.is_email_verified
                },
                'csrf_token': session.get('_csrf_token')
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        current_app.logger.error(f"Session check error: {str(e)}")
        return jsonify({'error': 'Session check failed'}), 500

@api_auth_bp.route('/auth/refresh-session', methods=['POST'])
@login_required
def refresh_session():
    """API endpoint to refresh user session."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # Update last activity
        current_user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate new CSRF token
        session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Session refreshed successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'last_login': current_user.last_login.isoformat()
            },
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Session refresh error: {str(e)}")
        return jsonify({'error': 'Session refresh failed'}), 500

@api_auth_bp.route('/auth/csrf-token', methods=['GET'])
def get_csrf_token():
    """API endpoint to get CSRF token."""
    try:
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"CSRF token error: {str(e)}")
        return jsonify({'error': 'Failed to get CSRF token'}), 500