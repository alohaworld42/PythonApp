#!/usr/bin/env python3

# Create a minimal auth.py to test
import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Test creating a simple auth blueprint
from flask import Blueprint

print("Creating simple auth blueprint...")

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test')
def test():
    return "Test"

print(f"Blueprint created: {auth_bp}")
print(f"Blueprint name: {auth_bp.name}")

# Now test importing it
print("Testing import...")
try:
    # Save current auth.py
    if os.path.exists('app/routes/auth_backup.py'):
        os.remove('app/routes/auth_backup.py')
    
    if os.path.exists('app/routes/auth.py'):
        os.rename('app/routes/auth.py', 'app/routes/auth_backup.py')
    
    # Create simple auth.py
    with open('app/routes/auth.py', 'w') as f:
        f.write('''from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test')
def test():
    return "Test"
''')
    
    # Test import
    from app.routes.auth import auth_bp as test_bp
    print(f"✓ Simple auth blueprint imported successfully: {test_bp.name}")
    
    # Restore original
    os.remove('app/routes/auth.py')
    if os.path.exists('app/routes/auth_backup.py'):
        os.rename('app/routes/auth_backup.py', 'app/routes/auth.py')
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    # Restore original if error
    if os.path.exists('app/routes/auth_backup.py'):
        if os.path.exists('app/routes/auth.py'):
            os.remove('app/routes/auth.py')
        os.rename('app/routes/auth_backup.py', 'app/routes/auth.py')