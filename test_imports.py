#!/usr/bin/env python3

# Test imports one by one to find the issue

try:
    from flask import Blueprint
    print("✓ Flask Blueprint imported successfully")
except ImportError as e:
    print(f"✗ Flask Blueprint import failed: {e}")

try:
    from app.models.user import User
    print("✓ User model imported successfully")
except ImportError as e:
    print(f"✗ User model import failed: {e}")

try:
    from app.utils.forms import LoginForm
    print("✓ Forms imported successfully")
except ImportError as e:
    print(f"✗ Forms import failed: {e}")

try:
    from app.utils.oauth import OAuthSignIn
    print("✓ OAuth imported successfully")
except ImportError as e:
    print(f"✗ OAuth import failed: {e}")

try:
    from app.utils.email import send_password_reset_email
    print("✓ Email utils imported successfully")
except ImportError as e:
    print(f"✗ Email utils import failed: {e}")

try:
    from app import db, bcrypt
    print("✓ App extensions imported successfully")
except ImportError as e:
    print(f"✗ App extensions import failed: {e}")

# Now try to import the auth blueprint
try:
    from app.routes.auth import auth_bp
    print("✓ Auth blueprint imported successfully")
except ImportError as e:
    print(f"✗ Auth blueprint import failed: {e}")