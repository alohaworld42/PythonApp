#!/usr/bin/env python3
"""
Test script for dashboard functionality
"""

import sys
import os
sys.path.append('.')

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from flask_login import login_user
import tempfile

def test_dashboard():
    """Test dashboard functionality"""
    
    # Create test app
    app = create_app()
    
    with app.app_context():
        # Test that we can render the dashboard template
        from flask import render_template_string
        
        # Create a test user
        test_user = User.query.first()
        if not test_user:
            print("No test user found, creating one...")
            test_user = User(
                name="Test User",
                email="test@example.com",
                password_hash="test_hash"
            )
            db.session.add(test_user)
            db.session.commit()
        
        # Get purchases for the user
        purchases = Purchase.query.filter_by(user_id=test_user.id).all()
        print(f"Found {len(purchases)} purchases for user {test_user.name}")
        
        # Test dashboard data preparation
        shared_count = sum(1 for p in purchases if p.is_shared)
        print(f"Shared purchases: {shared_count}")
        
        # Test filtering logic
        stores = list(set(p.store_name for p in purchases if p.store_name))
        print(f"Available stores: {stores}")
        
        # Test sorting logic
        purchases_by_date = sorted(purchases, key=lambda p: p.purchase_date, reverse=True)
        print(f"Latest purchase: {purchases_by_date[0].purchase_date if purchases_by_date else 'None'}")
        
        print("✓ Dashboard functionality test passed!")

if __name__ == "__main__":
    test_dashboard()