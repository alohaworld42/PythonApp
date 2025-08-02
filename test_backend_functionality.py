#!/usr/bin/env python3
"""
Comprehensive Backend Functionality Test for BuyRoll
Tests all database operations, API endpoints, and data integrity
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import traceback

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.models.interaction import Interaction
from config import TestingConfig

class BackendTester:
    def __init__(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Test data
        self.test_users = []
        self.test_products = []
        self.test_purchases = []
        self.csrf_token = None
        
        # Results tracking
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        result = f"[{status}] {test_name}"
        if message:
            result += f" - {message}"
        
        print(result)
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    def setup_database(self):
        """Setup test database"""
        try:
            db.create_all()
            self.log_test("Database Setup", True, "Tables created successfully")
            return True
        except Exception as e:
            self.log_test("Database Setup", False, f"Error: {str(e)}")
            return False

    def test_database_models(self):
        """Test database model creation and relationships"""
        try:
            # Test User model
            user = User(
                email="test@example.com",
                name="Test User",
                password_hash=User.hash_password("testpassword123"),
                is_email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            self.test_users.append(user)
            
            # Test Product model
            product = Product(
                external_id="test-product-1",
                source="test",
                title="Test Product",
                description="A test product for testing",
                image_url="https://example.com/image.jpg",
                price=29.99,
                currency="USD",
                category="Electronics"
            )
            db.session.add(product)
            db.session.commit()
            self.test_products.append(product)
            
            # Test Purchase model
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name="Test Store",
                order_id="TEST-ORDER-123",
                is_shared=True,
                share_comment="Great product!"
            )
            db.session.add(purchase)
            db.session.commit()
            self.test_purchases.append(purchase)
            
            # Test relationships
            assert user.purchases[0].id == purchase.id
            assert purchase.user.id == user.id
            assert purchase.product.id == product.id
            
            self.log_test("Database Models", True, "All models and relationships work correctly")
            return True
            
        except Exception as e:
            self.log_test("Database Models", False, f"Error: {str(e)}")
            return False

    def test_user_authentication(self):
        """Test user authentication functionality"""
        try:
            # Test password hashing
            password = "testpassword123"
            hashed = User.hash_password(password)
            
            user = User.query.filter_by(email="test@example.com").first()
            assert user.check_password(password)
            assert not user.check_password("wrongpassword")
            
            # Test token generation
            token = user.get_reset_token()
            assert token is not None
            
            # Test token verification
            verified_user = User.verify_reset_token(token)
            assert verified_user.id == user.id
            
            self.log_test("User Authentication", True, "Password hashing and tokens work correctly")
            return True
            
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    def get_csrf_token(self):
        """Get CSRF token for API requests"""
        try:
            response = self.client.get('/api/auth/csrf-token')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.csrf_token = data['csrf_token']
                return True
            return False
        except:
            return False

    def test_auth_api_endpoints(self):
        """Test authentication API endpoints"""
        try:
            # Get CSRF token
            if not self.get_csrf_token():
                self.log_test("Auth API - CSRF Token", False, "Failed to get CSRF token")
                return False
            
            # Test user registration
            register_data = {
                'email': 'newuser@example.com',
                'password': 'newpassword123',
                'name': 'New User',
                '_csrf_token': self.csrf_token
            }
            
            response = self.client.post('/api/auth/register', 
                                      json=register_data,
                                      headers={'X-CSRF-Token': self.csrf_token})
            
            if response.status_code == 201:
                self.log_test("Auth API - Registration", True, "User registration successful")
            else:
                self.log_test("Auth API - Registration", False, f"Status: {response.status_code}")
                return False
            
            # Test user login
            login_data = {
                'email': 'newuser@example.com',
                'password': 'newpassword123',
                '_csrf_token': self.csrf_token
            }
            
            response = self.client.post('/api/auth/login',
                                      json=login_data,
                                      headers={'X-CSRF-Token': self.csrf_token})
            
            if response.status_code == 200:
                self.log_test("Auth API - Login", True, "User login successful")
                # Update CSRF token from login response
                data = json.loads(response.data)
                self.csrf_token = data.get('csrf_token', self.csrf_token)
            else:
                self.log_test("Auth API - Login", False, f"Status: {response.status_code}")
                return False
            
            # Test getting current user
            response = self.client.get('/api/auth/me')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert data['user']['email'] == 'newuser@example.com'
                self.log_test("Auth API - Get Current User", True, "User info retrieved successfully")
            else:
                self.log_test("Auth API - Get Current User", False, f"Status: {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Auth API Endpoints", False, f"Error: {str(e)}")
            return False

    def test_purchase_sharing_api(self):
        """Test purchase sharing API endpoints"""
        try:
            # First, create some test data
            with self.app.app_context():
                # Create a test user and product for API testing
                api_user = User(
                    email="apiuser@example.com",
                    name="API User",
                    password_hash=User.hash_password("apipassword123"),
                    is_email_verified=True
                )
                db.session.add(api_user)
                
                api_product = Product(
                    external_id="api-product-1",
                    source="api-test",
                    title="API Test Product",
                    description="Product for API testing",
                    image_url="https://example.com/api-image.jpg",
                    price=49.99,
                    currency="USD",
                    category="Test"
                )
                db.session.add(api_product)
                db.session.commit()
                
                api_purchase = Purchase(
                    user_id=api_user.id,
                    product_id=api_product.id,
                    store_name="API Test Store",
                    order_id="API-ORDER-123",
                    is_shared=True,
                    share_comment="API test purchase"
                )
                db.session.add(api_purchase)
                db.session.commit()
            
            # Test getting purchases (should work with logged in user)
            response = self.client.get('/api/purchases')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'purchases' in data
                assert 'pagination' in data
                self.log_test("Purchase API - Get Purchases", True, "Purchases retrieved successfully")
            else:
                self.log_test("Purchase API - Get Purchases", False, f"Status: {response.status_code}")
            
            # Test getting feed
            response = self.client.get('/api/feed')
            
            if response.status_code == 200:
                data = json.loads(response.data)
                assert 'feed' in data
                assert 'pagination' in data
                self.log_test("Purchase API - Get Feed", True, "Feed retrieved successfully")
            else:
                self.log_test("Purchase API - Get Feed", False, f"Status: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_test("Purchase Sharing API", False, f"Error: {str(e)}")
            return False

    def test_database_integrity(self):
        """Test database integrity and constraints"""
        try:
            # Test unique constraints
            try:
                duplicate_user = User(
                    email="test@example.com",  # Same email as existing user
                    name="Duplicate User",
                    password_hash=User.hash_password("password123"),
                    is_email_verified=True
                )
                db.session.add(duplicate_user)
                db.session.commit()
                # If we get here, the unique constraint failed
                self.log_test("Database Integrity - Unique Constraints", False, "Duplicate email allowed")
                return False
            except Exception:
                # This is expected - rollback and continue
                db.session.rollback()
                self.log_test("Database Integrity - Unique Constraints", True, "Unique constraints working")
            
            # Test foreign key constraints
            try:
                invalid_purchase = Purchase(
                    user_id=99999,  # Non-existent user
                    product_id=99999,  # Non-existent product
                    store_name="Invalid Store",
                    order_id="INVALID-ORDER"
                )
                db.session.add(invalid_purchase)
                db.session.commit()
                # If we get here, foreign key constraints failed
                self.log_test("Database Integrity - Foreign Keys", False, "Invalid foreign keys allowed")
                return False
            except Exception:
                # This is expected - rollback and continue
                db.session.rollback()
                self.log_test("Database Integrity - Foreign Keys", True, "Foreign key constraints working")
            
            # Test data validation
            user = User.query.first()
            original_email = user.email
            
            # Test email validation would be done at application level
            # Here we test that the model accepts valid data
            user.email = "valid@example.com"
            db.session.commit()
            
            user.email = original_email
            db.session.commit()
            
            self.log_test("Database Integrity - Data Validation", True, "Data validation working")
            return True
            
        except Exception as e:
            self.log_test("Database Integrity", False, f"Error: {str(e)}")
            return False

    def test_relationships_and_queries(self):
        """Test database relationships and complex queries"""
        try:
            # Test user-purchase relationship
            user = User.query.first()
            user_purchases = user.purchases
            assert len(user_purchases) > 0
            
            # Test purchase-product relationship
            purchase = Purchase.query.first()
            product = purchase.product
            assert product is not None
            assert product.title is not None
            
            # Test complex queries
            # Get shared purchases
            shared_purchases = Purchase.query.filter_by(is_shared=True).all()
            assert len(shared_purchases) > 0
            
            # Get purchases by price range
            expensive_products = Product.query.filter(Product.price > 25.0).all()
            assert len(expensive_products) > 0
            
            # Test joins
            user_product_query = db.session.query(User, Product, Purchase).join(
                Purchase, User.id == Purchase.user_id
            ).join(
                Product, Purchase.product_id == Product.id
            ).all()
            
            assert len(user_product_query) > 0
            
            self.log_test("Database Relationships", True, "All relationships and queries working")
            return True
            
        except Exception as e:
            self.log_test("Database Relationships", False, f"Error: {str(e)}")
            return False

    def test_data_persistence(self):
        """Test that data persists correctly"""
        try:
            # Count initial records
            initial_users = User.query.count()
            initial_products = Product.query.count()
            initial_purchases = Purchase.query.count()
            
            # Add new records
            new_user = User(
                email="persistence@example.com",
                name="Persistence Test",
                password_hash=User.hash_password("persisttest123"),
                is_email_verified=True
            )
            db.session.add(new_user)
            db.session.commit()
            
            new_product = Product(
                external_id="persist-product",
                source="persistence-test",
                title="Persistence Product",
                description="Testing data persistence",
                price=15.99,
                currency="USD",
                category="Test"
            )
            db.session.add(new_product)
            db.session.commit()
            
            new_purchase = Purchase(
                user_id=new_user.id,
                product_id=new_product.id,
                store_name="Persistence Store",
                is_shared=False
            )
            db.session.add(new_purchase)
            db.session.commit()
            
            # Verify counts increased
            final_users = User.query.count()
            final_products = Product.query.count()
            final_purchases = Purchase.query.count()
            
            assert final_users == initial_users + 1
            assert final_products == initial_products + 1
            assert final_purchases == initial_purchases + 1
            
            # Verify data integrity
            retrieved_user = User.query.filter_by(email="persistence@example.com").first()
            assert retrieved_user is not None
            assert retrieved_user.name == "Persistence Test"
            
            retrieved_purchase = Purchase.query.filter_by(user_id=new_user.id, product_id=new_product.id).first()
            assert retrieved_purchase is not None
            assert retrieved_purchase.store_name == "Persistence Store"
            
            self.log_test("Data Persistence", True, "Data persists correctly")
            return True
            
        except Exception as e:
            self.log_test("Data Persistence", False, f"Error: {str(e)}")
            return False

    def test_error_handling(self):
        """Test error handling in API endpoints"""
        try:
            # Test invalid login
            response = self.client.post('/api/auth/login', json={
                'email': 'nonexistent@example.com',
                'password': 'wrongpassword',
                '_csrf_token': self.csrf_token
            }, headers={'X-CSRF-Token': self.csrf_token})
            
            assert response.status_code == 401
            
            # Test missing CSRF token
            response = self.client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'password'
            })
            
            assert response.status_code == 403
            
            # Test invalid data
            response = self.client.post('/api/auth/register', json={
                'email': 'invalid-email',
                'password': '123',  # Too short
                'name': '',  # Empty name
                '_csrf_token': self.csrf_token
            }, headers={'X-CSRF-Token': self.csrf_token})
            
            assert response.status_code == 400
            
            self.log_test("Error Handling", True, "API error handling working correctly")
            return True
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False

    def cleanup_database(self):
        """Clean up test database"""
        try:
            db.drop_all()
            self.log_test("Database Cleanup", True, "Test database cleaned up")
            return True
        except Exception as e:
            self.log_test("Database Cleanup", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("BUYROLL BACKEND FUNCTIONALITY TEST")
        print("=" * 60)
        print()
        
        # Setup
        if not self.setup_database():
            print("Database setup failed. Aborting tests.")
            return False
        
        # Run tests
        tests = [
            self.test_database_models,
            self.test_user_authentication,
            self.test_auth_api_endpoints,
            self.test_purchase_sharing_api,
            self.test_database_integrity,
            self.test_relationships_and_queries,
            self.test_data_persistence,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Unexpected error: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
        
        # Cleanup
        self.cleanup_database()
        
        # Summary
        print()
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.passed_tests + self.failed_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        if self.failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['name']}: {result['message']}")
        
        print()
        return self.failed_tests == 0

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

def main():
    """Main function to run backend tests"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All backend functionality tests passed!")
        return 0
    else:
        print("❌ Some backend tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())