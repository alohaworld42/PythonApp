import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase

class TestAnalyticsAPI(unittest.TestCase):
    """Test cases for the Analytics API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create tables
        db.create_all()
        
        # Create test user
        self.user = User(
            email='test@example.com',
            name='Test User',
            password_hash='hashed_password'
        )
        db.session.add(self.user)
        db.session.commit()
        
        # Create test products and purchases
        self.setup_test_data()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def setup_test_data(self):
        """Set up test products and purchases."""
        # Create test products
        products = [
            Product(
                title='Laptop',
                source='shopify',
                price=999.99,
                currency='USD',
                category='Electronics'
            ),
            Product(
                title='T-Shirt',
                source='woocommerce',
                price=29.99,
                currency='USD',
                category='Clothing'
            ),
            Product(
                title='Coffee Maker',
                source='shopify',
                price=149.99,
                currency='USD',
                category='Home'
            )
        ]
        
        for product in products:
            db.session.add(product)
        db.session.commit()
        
        # Create test purchases
        now = datetime.now()
        purchases = [
            Purchase(
                user_id=self.user.id,
                product_id=products[0].id,
                purchase_date=now - timedelta(days=30),
                store_name='Tech Store',
                order_id='ORDER001'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=products[1].id,
                purchase_date=now - timedelta(days=60),
                store_name='Fashion Store',
                order_id='ORDER002'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=products[2].id,
                purchase_date=now - timedelta(days=15),
                store_name='Home Store',
                order_id='ORDER003'
            )
        ]
        
        for purchase in purchases:
            db.session.add(purchase)
        db.session.commit()
    
    def login_user(self):
        """Helper method to log in the test user."""
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.user.id)
            sess['_fresh'] = True
    
    def test_get_spending_analytics(self):
        """Test the spending analytics API endpoint."""
        self.login_user()
        
        response = self.client.get('/api/analytics/spending')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('monthly_spending', data)
        self.assertIn('total_months', data)
    
    def test_get_category_analytics(self):
        """Test the category analytics API endpoint."""
        self.login_user()
        
        response = self.client.get('/api/analytics/categories')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('category_analysis', data)
        self.assertIn('total_spending', data)
        self.assertIn('total_categories', data)
    
    def test_get_store_analytics(self):
        """Test the store analytics API endpoint."""
        self.login_user()
        
        response = self.client.get('/api/analytics/stores')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('store_analysis', data)
        self.assertIn('total_spending', data)
        self.assertIn('total_stores', data)
    
    def test_get_trend_analytics(self):
        """Test the trend analytics API endpoint."""
        self.login_user()
        
        response = self.client.get('/api/analytics/trends')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('trends_data', data)
        self.assertIn('period_months', data)
        self.assertIn('statistics', data)
    
    def test_get_comprehensive_analytics(self):
        """Test the comprehensive analytics API endpoint."""
        self.login_user()
        
        response = self.client.get('/api/analytics/comprehensive')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('monthly_spending', data)
        self.assertIn('category_analysis', data)
        self.assertIn('store_analysis', data)
        self.assertIn('spending_trends', data)
        self.assertIn('period', data)
    
    def test_analytics_with_parameters(self):
        """Test analytics endpoints with query parameters."""
        self.login_user()
        
        # Test with period_months parameter
        response = self.client.get('/api/analytics/categories?period_months=6')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/api/analytics/stores?period_months=6')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/api/analytics/trends?period_months=6')
        self.assertEqual(response.status_code, 200)
        
        # Test spending with year/month parameters
        current_year = datetime.now().year
        response = self.client.get(f'/api/analytics/spending?year={current_year}')
        self.assertEqual(response.status_code, 200)
    
    def test_unauthorized_access(self):
        """Test that analytics endpoints require authentication."""
        # Don't log in the user
        
        endpoints = [
            '/api/analytics/spending',
            '/api/analytics/categories',
            '/api/analytics/stores',
            '/api/analytics/trends',
            '/api/analytics/comprehensive'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Flask-Login redirects to login page (302) when not authenticated
            self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()