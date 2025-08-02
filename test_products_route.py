#!/usr/bin/env python3
"""
Simple test to verify the products route works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    
    app = create_app()
    
    with app.test_client() as client:
        # Test the products route
        response = client.get('/products')
        print(f"Products route status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Products route is working correctly!")
            print(f"Response length: {len(response.data)} bytes")
            
            # Check if the response contains expected content
            content = response.data.decode('utf-8')
            if 'Discover Amazing Products' in content:
                print("✅ Products page contains expected header")
            if 'Premium Wireless Headphones' in content:
                print("✅ Products page contains sample products")
            if 'Newsletter' in content:
                print("✅ Products page contains newsletter section")
                
        else:
            print(f"❌ Products route failed with status {response.status_code}")
            
except Exception as e:
    print(f"❌ Error testing products route: {e}")