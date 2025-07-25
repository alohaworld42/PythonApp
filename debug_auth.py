#!/usr/bin/env python3

# Debug auth.py imports step by step

print("Testing imports from auth.py...")

try:
    from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
    print("✓ Flask imports successful")
except ImportError as e:
    print(f"✗ Flask imports failed: {e}")
    exit(1)

try:
    from flask_login import login_user, logout_user, current_user, login_required
    print("✓ Flask-Login imports successful")
except ImportError as e:
    print(f"✗ Flask-Login imports failed: {e}")
    exit(1)

try:
    import hmac
    print("✓ hmac import successful")
except ImportError as e:
    print(f"✗ hmac import failed: {e}")
    exit(1)

try:
    from app import db, bcrypt
    print("✓ App extensions import successful")
except ImportError as e:
    print(f"✗ App extensions import failed: {e}")
    exit(1)

try:
    from app.models.user import User
    print("✓ User model import successful")
except ImportError as e:
    print(f"✗ User model import failed: {e}")
    exit(1)

try:
    from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestResetForm
    print("✓ Forms import successful")
except ImportError as e:
    print(f"✗ Forms import failed: {e}")
    exit(1)

try:
    from app.utils.oauth import OAuthSignIn, process_oauth_login
    print("✓ OAuth import successful")
except ImportError as e:
    print(f"✗ OAuth import failed: {e}")
    exit(1)

try:
    from app.utils.email import send_password_reset_email, send_email_verification
    print("✓ Email utils import successful")
except ImportError as e:
    print(f"✗ Email utils import failed: {e}")
    exit(1)

try:
    from datetime import datetime, timedelta
    import secrets
    print("✓ Standard library imports successful")
except ImportError as e:
    print(f"✗ Standard library imports failed: {e}")
    exit(1)

# Now try to create the blueprint
try:
    auth_bp = Blueprint('auth', __name__)
    print("✓ Blueprint creation successful")
    print(f"Blueprint name: {auth_bp.name}")
except Exception as e:
    print(f"✗ Blueprint creation failed: {e}")
    exit(1)

print("All imports successful! The issue might be elsewhere in the auth.py file.")