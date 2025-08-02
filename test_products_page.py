#!/usr/bin/env python3
"""
Test script to check if the products page is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_products_page():
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            print("Testing products page...")
            
            # Test the products route
            response = client.get('/products')
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                content = response.data.decode('utf-8')
                print(f"Response length: {len(content)} characters")
                
                # Check for key elements
                checks = [
                    ('Header found', 'Discover Amazing' in content and 'Products' in content),
                    ('Sample products found', 'Premium Wireless Headphones' in content),
                    ('Layout template used', 'layout_clean.html' in content or 'container' in content),
                    ('CSS classes present', 'bg-gradient-to-br' in content),
                    ('JavaScript present', 'addEventListener' in content),
                    ('Newsletter section', 'Newsletter' in content or 'Subscribe' in content)
                ]
                
                print("\n=== Content Analysis ===")
                for check_name, result in checks:
                    status = "✅" if result else "❌"
                    print(f"{status} {check_name}")
                
                # Show first 500 characters of response
                print(f"\n=== First 500 characters of response ===")
                print(content[:500])
                print("...")
                
                # Check if template is being rendered correctly
                if 'layout_clean.html' not in content and 'DOCTYPE html' in content:
                    print("✅ HTML template is being rendered")
                else:
                    print("❌ Template rendering issue detected")
                    
            else:
                print(f"❌ Products page failed with status {response.status_code}")
                print("Response:", response.data.decode('utf-8')[:200])
                
    except Exception as e:
        print(f"❌ Error testing products page: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_products_page()