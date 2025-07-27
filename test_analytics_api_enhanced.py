#!/usr/bin/env python3
"""
Enhanced test suite for analytics API endpoints.
Tests all analytics functionality including spending, categories, stores, trends, and insights.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase

class TestAnalyticsAPI:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        
    def setup(self):
        """Set up test environment."""
        self.app_context.push()
        db.create_all()
        
    def teardown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def get_csrf_token(self):
        """Get CSRF token for API requests."""
        response = self.client.get('/api/auth/csrf-token')
        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('csrf_token')
        return None
        
    def login_user(self, email, password):
        """Helper method to login a user and return CSRF token."""
        csrf_token = self.get_csrf_token()
        
        login_data = {
            'email': email,
            'password': password,
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/auth/login',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            return data.get('csrf_token')
        return None
        
    def create_test_data(self):
        """Create comprehensive test data for analytics."""
        # Create user
        user = User(
            name='Analytics Test User',
            email='analytics@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        
        # Create products in different categories
        products = [
            Product(
                external_id='prod1',
                source='shopify',
                title='Laptop',
                description='Gaming laptop',
                image_url='https://example.com/laptop.jpg',
                price=Decimal('1200.00'),
                currency='USD',
                category='Electronics'
            ),
            Product(
                external_id='prod2',
                source='woocommerce',
                title='T-Shirt',
                description='Cotton t-shirt',
                image_url='https://example.com/tshirt.jpg',
                price=Decimal('25.00'),
                currency='USD',
                category='Clothing'
            ),
            Product(
                external_id='prod3',
                source='shopify',
                title='Coffee Maker',
                description='Automatic coffee maker',
                image_url='https://example.com/coffee.jpg',
                price=Decimal('150.00'),
                currency='USD',
                category='Home & Kitchen'
            ),
            Product(
                external_id='prod4',
                source='woocommerce',
                title='Smartphone',
                description='Latest smartphone',
                image_url='https://example.com/phone.jpg',
                price=Decimal('800.00'),
                currency='USD',
                category='Electronics'
            ),
            Product(
                external_id='prod5',
                source='shopify',
                title='Jeans',
                description='Blue jeans',
                image_url='https://example.com/jeans.jpg',
                price=Decimal('60.00'),
                currency='USD',
                category='Clothing'
            )
        ]
        
        for product in products:
            db.session.add(product)
        db.session.commit()
        
        # Create purchases across different months and stores
        now = datetime.now()
        purchases = [
            # Current month
            Purchase(
                user_id=user.id,
                product_id=products[0].id,  # Laptop
                purchase_date=now - timedelta(days=5),
                store_name='TechStore',
                order_id='ORDER001',
                is_shared=True
            ),
            Purchase(
                user_id=user.id,
                product_id=products[1].id,  # T-Shirt
                purchase_date=now - timedelta(days=3),
                store_name='ClothingStore',
                order_id='ORDER002',
                is_shared=False
            ),
            # Last month
            Purchase(
                user_id=user.id,
                product_id=products[2].id,  # Coffee Maker
                purchase_date=now - timedelta(days=35),
                store_name='HomeStore',
                order_id='ORDER003',
                is_shared=True
            ),
            Purchase(
                user_id=user.id,
                product_id=products[3].id,  # Smartphone
                purchase_date=now - timedelta(days=40),
                store_name='TechStore',
                order_id='ORDER004',
                is_shared=True
            ),
            # Two months ago
            Purchase(
                user_id=user.id,
                product_id=products[4].id,  # Jeans
                purchase_date=now - timedelta(days=65),
                store_name='ClothingStore',
                order_id='ORDER005',
                is_shared=False
            )
        ]
        
        for purchase in purchases:
            db.session.add(purchase)
        db.session.commit()
        
        return {
            'user': user,
            'products': products,
            'purchases': purchases
        }
        
    def test_spending_analytics(self):
        """Test monthly spending analytics endpoint."""
        print("Testing spending analytics...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get all monthly spending
        response = self.client.get('/api/analytics/spending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'monthly_spending' in data['data']
        assert len(data['data']['monthly_spending']) >= 1
        
        # Test filter by current year
        current_year = datetime.now().year
        response = self.client.get(f'/api/analytics/spending?year={current_year}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['filters']['year'] == current_year
        
        # Test filter by specific month
        current_month = datetime.now().month
        response = self.client.get(f'/api/analytics/spending?year={current_year}&month={current_month}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['filters']['month'] == current_month
        
        # Test invalid year
        response = self.client.get('/api/analytics/spending?year=1999')
        assert response.status_code == 400
        
        # Test invalid month
        response = self.client.get('/api/analytics/spending?month=13')
        assert response.status_code == 400
        
        print("✓ Spending analytics works correctly")
        
    def test_category_analytics(self):
        """Test category-based spending analytics endpoint."""
        print("Testing category analytics...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get category analytics
        response = self.client.get('/api/analytics/categories')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'category_analysis' in data['data']
        assert len(data['data']['category_analysis']) >= 1
        
        # Verify category data structure
        category = data['data']['category_analysis'][0]
        assert 'category' in category
        assert 'total_spending' in category
        assert 'purchase_count' in category
        assert 'percentage' in category
        
        # Test with custom period
        response = self.client.get('/api/analytics/categories?period_months=6')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['filters']['period_months'] == 6
        
        # Test with custom date range
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        response = self.client.get(f'/api/analytics/categories?start_date={start_date}&end_date={end_date}')
        assert response.status_code == 200
        
        # Test invalid period
        response = self.client.get('/api/analytics/categories?period_months=100')
        assert response.status_code == 400
        
        print("✓ Category analytics works correctly")
        
    def test_store_analytics(self):
        """Test store-based spending analytics endpoint."""
        print("Testing store analytics...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get store analytics
        response = self.client.get('/api/analytics/stores')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'store_analysis' in data['data']
        assert len(data['data']['store_analysis']) >= 1
        
        # Verify store data structure
        store = data['data']['store_analysis'][0]
        assert 'store_name' in store
        assert 'total_spending' in store
        assert 'purchase_count' in store
        assert 'percentage' in store
        assert 'last_purchase' in store
        
        # Test with custom period
        response = self.client.get('/api/analytics/stores?period_months=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['filters']['period_months'] == 3
        
        print("✓ Store analytics works correctly")
        
    def test_trend_analytics(self):
        """Test spending trend analytics endpoint."""
        print("Testing trend analytics...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get trend analytics
        response = self.client.get('/api/analytics/trends')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'trends_data' in data['data']
        assert 'statistics' in data['data']
        
        # Verify statistics structure
        stats = data['data']['statistics']
        assert 'avg_monthly_spending' in stats
        assert 'max_monthly_spending' in stats
        assert 'min_monthly_spending' in stats
        assert 'total_spending' in stats
        assert 'trend_direction' in stats
        assert stats['trend_direction'] in ['increasing', 'decreasing', 'stable']
        
        # Test with custom period
        response = self.client.get('/api/analytics/trends?period_months=6')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['filters']['period_months'] == 6
        
        print("✓ Trend analytics works correctly")
        
    def test_comprehensive_analytics(self):
        """Test comprehensive analytics endpoint."""
        print("Testing comprehensive analytics...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get comprehensive analytics
        response = self.client.get('/api/analytics/comprehensive')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        
        # Verify all analytics sections are present
        analytics_data = data['data']
        assert 'monthly_spending' in analytics_data
        assert 'category_analysis' in analytics_data
        assert 'store_analysis' in analytics_data
        assert 'spending_trends' in analytics_data
        assert 'period' in analytics_data
        
        # Verify period information
        period = analytics_data['period']
        assert 'start_date' in period
        assert 'end_date' in period
        assert 'months' in period
        
        print("✓ Comprehensive analytics works correctly")
        
    def test_analytics_summary(self):
        """Test analytics summary endpoint."""
        print("Testing analytics summary...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get analytics summary
        response = self.client.get('/api/analytics/summary')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        
        # Verify summary structure
        summary = data['data']
        assert 'total_statistics' in summary
        assert 'current_month' in summary
        assert 'month_comparison' in summary
        
        # Verify total statistics
        total_stats = summary['total_statistics']
        assert 'total_purchases' in total_stats
        assert 'total_spending' in total_stats
        assert 'avg_purchase_price' in total_stats
        
        # Verify current month data
        current_month = summary['current_month']
        assert 'purchases' in current_month
        assert 'spending' in current_month
        
        # Verify month comparison
        comparison = summary['month_comparison']
        assert 'change_amount' in comparison
        assert 'change_percentage' in comparison
        assert 'trend' in comparison
        assert comparison['trend'] in ['up', 'down', 'stable']
        
        print("✓ Analytics summary works correctly")
        
    def test_spending_insights(self):
        """Test spending insights endpoint."""
        print("Testing spending insights...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test get spending insights
        response = self.client.get('/api/analytics/insights')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        
        # Verify insights structure
        insights_data = data['data']
        assert 'insights' in insights_data
        assert 'analysis_period' in insights_data
        assert 'summary_stats' in insights_data
        
        # Verify insights format
        insights = insights_data['insights']
        if len(insights) > 0:
            insight = insights[0]
            assert 'type' in insight
            assert 'level' in insight
            assert 'title' in insight
            assert 'message' in insight
            assert 'recommendation' in insight
            assert insight['level'] in ['info', 'warning', 'positive', 'suggestion']
        
        # Test with custom period
        response = self.client.get('/api/analytics/insights?period_months=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['data']['analysis_period']['months'] == 3
        
        print("✓ Spending insights works correctly")
        
    def test_analytics_export(self):
        """Test analytics export endpoint."""
        print("Testing analytics export...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('analytics@example.com', 'TestPassword123')
        
        # Test JSON export (default)
        response = self.client.get('/api/analytics/export')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'export_info' in data
        assert data['export_info']['format'] == 'json'
        
        # Test CSV export
        response = self.client.get('/api/analytics/export?format=csv')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['export_info']['format'] == 'csv'
        
        # Test invalid format
        response = self.client.get('/api/analytics/export?format=xml')
        assert response.status_code == 400
        
        # Test with custom period
        response = self.client.get('/api/analytics/export?period_months=6')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['export_info']['period_months'] == 6
        
        print("✓ Analytics export works correctly")
        
    def run_all_tests(self):
        """Run all analytics API tests."""
        print("=" * 60)
        print("RUNNING ENHANCED ANALYTICS API TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_spending_analytics()
            self.test_category_analytics()
            self.test_store_analytics()
            self.test_trend_analytics()
            self.test_comprehensive_analytics()
            self.test_analytics_summary()
            self.test_spending_insights()
            self.test_analytics_export()
            
            print("\n" + "=" * 60)
            print("✅ ALL ENHANCED ANALYTICS API TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.teardown()

if __name__ == '__main__':
    tester = TestAnalyticsAPI()
    tester.run_all_tests()