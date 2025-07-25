#!/usr/bin/env python3

# Debug auth.py step by step

print("Step 1: Testing basic imports...")
try:
    from flask import Blueprint
    print("✓ Flask Blueprint imported")
except Exception as e:
    print(f"✗ Flask Blueprint failed: {e}")
    exit(1)

print("Step 2: Testing app imports...")
try:
    from app import db, bcrypt
    print("✓ App imports successful")
except Exception as e:
    print(f"✗ App imports failed: {e}")
    exit(1)

print("Step 3: Testing model imports...")
try:
    from app.models.user import User
    print("✓ User model imported")
except Exception as e:
    print(f"✗ User model failed: {e}")
    exit(1)

print("Step 4: Testing form imports...")
try:
    from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestResetForm
    print("✓ Forms imported")
except Exception as e:
    print(f"✗ Forms failed: {e}")
    exit(1)

print("Step 5: Creating blueprint...")
try:
    auth_bp = Blueprint('auth', __name__)
    print(f"✓ Blueprint created: {auth_bp}")
except Exception as e:
    print(f"✗ Blueprint creation failed: {e}")
    exit(1)

print("Step 6: Testing route creation...")
try:
    @auth_bp.route('/test')
    def test():
        return "test"
    print("✓ Route created")
except Exception as e:
    print(f"✗ Route creation failed: {e}")
    exit(1)

print("All steps successful!")