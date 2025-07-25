import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.services.analytics_service import AnalyticsService

class TestAnalyticsService(unittest.TestCase):
    """Test cases for the AnalyticsService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
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
        
        # Create test products
        self.products = [
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
            ),
            Product(
                title='Headphones',
                source='shopify',
                price=199.99,
                currency='USD',
                category='Electronics'
            ),
            Product(
                title='Jeans',
                source='woocommerce',
                price=79.99,
                currency='USD',
                category='Clothing'
            )
        ]
        
        for product in self.products:
            db.session.add(product)
        db.session.commit()
        
        # Create test purchases with different dates
        now = datetime.now()
        self.purchases = [
            Purchase(
                user_id=self.user.id,
                product_id=self.products[0].id,  # Laptop
                purchase_date=now - timedelta(days=30),
                store_name='Tech Store',
                order_id='ORDER001'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=self.products[1].id,  # T-Shirt
                purchase_date=now - timedelta(days=60),
                store_name='Fashion Store',
                order_id='ORDER002'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=self.products[2].id,  # Coffee Maker
                purchase_date=now - timedelta(days=15),
                store_name='Home Store',
                order_id='ORDER003'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=self.products[3].id,  # Headphones
                purchase_date=now - timedelta(days=45),
                store_name='Tech Store',
                order_id='ORDER004'
            ),
            Purchase(
                user_id=self.user.id,
                product_id=self.products[4].id,  # Jeans
                purchase_date=now - timedelta(days=20),
                store_name='Fashion Store',
                order_id='ORDER005'
            )
        ]
        
        for purchase in self.purchases:
            db.session.add(purchase)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_get_monthly_spending(self):
        """Test monthly spending calculation."""
        result = AnalyticsService.get_monthly_spending(self.user.id)
        
        # Should return monthly spending data
        self.assertIn('monthly_spending', result)
        self.assertIn('total_months', result)
        self.assertIsInstance(result['monthly_spending'], list)
        self.assertGreater(result['total_months'], 0)
        
        # Check that each month has required fields
        for month_data in result['monthly_spending']:
            self.assertIn('year', month_data)
            self.assertIn('month', month_data)
            self.assertIn('month_name', month_data)
            self.assertIn('total_spending', month_data)
            self.assertIn('purchase_count', month_data)
            self.assertIn('period', month_data)
    
    def test_get_category_spending_analysis(self):
        """Test category-based spending analysis."""
        result = AnalyticsService.get_category_spending_analysis(self.user.id)
        
        # Should return category analysis data
        self.assertIn('category_analysis', result)
        self.assertIn('total_spending', result)
        self.assertIn('total_categories', result)
        self.assertIsInstance(result['category_analysis'], list)
        
        # Should have categories from our test data
        categories = [item['category'] for item in result['category_analysis']]
        self.assertIn('Electronics', categories)
        self.assertIn('Clothing', categories)
        self.assertIn('Home', categories)
        
        # Check that each category has required fields
        for category_data in result['category_analysis']:
            self.assertIn('category', category_data)
            self.assertIn('total_spending', category_data)
            self.assertIn('purchase_count', category_data)
            self.assertIn('avg_price', category_data)
            self.assertIn('percentage', category_data)
            
        # Electronics should have highest spending (Laptop + Headphones)
        electronics_data = next(
            item for item in result['category_analysis'] 
            if item['category'] == 'Electronics'
        )
        expected_electronics_spending = 999.99 + 199.99  # Laptop + Headphones
        self.assertAlmostEqual(
            electronics_data['total_spending'], 
            expected_electronics_spending, 
            places=2
        )
    
    def test_get_store_spending_analysis(self):
        """Test store-based spending analysis."""
        result = AnalyticsService.get_store_spending_analysis(self.user.id)
        
        # Should return store analysis data
        self.assertIn('store_analysis', result)
        self.assertIn('total_spending', result)
        self.assertIn('total_stores', result)
        self.assertIsInstance(result['store_analysis'], list)
        
        # Should have stores from our test data
        stores = [item['store_name'] for item in result['store_analysis']]
        self.assertIn('Tech Store', stores)
        self.assertIn('Fashion Store', stores)
        self.assertIn('Home Store', stores)
        
        # Check that each store has required fields
        for store_data in result['store_analysis']:
            self.assertIn('store_name', store_data)
            self.assertIn('total_spending', store_data)
            self.assertIn('purchase_count', store_data)
            self.assertIn('avg_price', store_data)
            self.assertIn('percentage', store_data)
            self.assertIn('last_purchase', store_data)
        
        # Tech Store should have highest spending (Laptop + Headphones)
        tech_store_data = next(
            item for item in result['store_analysis'] 
            if item['store_name'] == 'Tech Store'
        )
        expected_tech_spending = 999.99 + 199.99  # Laptop + Headphones
        self.assertAlmostEqual(
            tech_store_data['total_spending'], 
            expected_tech_spending, 
            places=2
        )
    
    def test_get_spending_trends(self):
        """Test spending trends calculation."""
        result = AnalyticsService.get_spending_trends(self.user.id, period_months=6)
        
        # Should return trends data
        self.assertIn('trends_data', result)
        self.assertIn('period_months', result)
        self.assertIn('statistics', result)
        self.assertIsInstance(result['trends_data'], list)
        
        # Check statistics
        stats = result['statistics']
        self.assertIn('avg_monthly_spending', stats)
        self.assertIn('max_monthly_spending', stats)
        self.assertIn('min_monthly_spending', stats)
        self.assertIn('total_spending', stats)
        self.assertIn('trend_direction', stats)
        
        # Trend direction should be one of the expected values
        self.assertIn(stats['trend_direction'], ['increasing', 'decreasing', 'stable'])
        
        # Check that each trend data point has required fields
        for trend_data in result['trends_data']:
            self.assertIn('year', trend_data)
            self.assertIn('month', trend_data)
            self.assertIn('month_name', trend_data)
            self.assertIn('period', trend_data)
            self.assertIn('total_spending', trend_data)
            self.assertIn('purchase_count', trend_data)
    
    def test_get_comprehensive_analytics(self):
        """Test comprehensive analytics combining all analysis types."""
        result = AnalyticsService.get_comprehensive_analytics(self.user.id)
        
        # Should contain all analysis types
        self.assertIn('monthly_spending', result)
        self.assertIn('category_analysis', result)
        self.assertIn('store_analysis', result)
        self.assertIn('spending_trends', result)
        self.assertIn('period', result)
        
        # Check period information
        period = result['period']
        self.assertIn('start_date', period)
        self.assertIn('end_date', period)
        self.assertIn('months', period)
        
        # Each section should have the expected structure
        self.assertIn('monthly_spending', result['monthly_spending'])
        self.assertIn('category_analysis', result['category_analysis'])
        self.assertIn('store_analysis', result['store_analysis'])
        self.assertIn('trends_data', result['spending_trends'])
    
    def test_monthly_spending_with_filters(self):
        """Test monthly spending with year and month filters."""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Test with year filter
        result = AnalyticsService.get_monthly_spending(
            self.user.id, 
            year=current_year
        )
        
        # All results should be from the specified year
        for month_data in result['monthly_spending']:
            self.assertEqual(month_data['year'], current_year)
        
        # Test with year and month filter
        result = AnalyticsService.get_monthly_spending(
            self.user.id, 
            year=current_year, 
            month=current_month
        )
        
        # All results should be from the specified year and month
        for month_data in result['monthly_spending']:
            self.assertEqual(month_data['year'], current_year)
            self.assertEqual(month_data['month'], current_month)
    
    def test_analytics_with_date_range(self):
        """Test analytics with specific date ranges."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Test category analysis with date range
        result = AnalyticsService.get_category_spending_analysis(
            self.user.id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        # Should only include purchases within the date range
        self.assertIn('category_analysis', result)
        self.assertGreaterEqual(result['total_spending'], 0)
        
        # Test store analysis with date range
        result = AnalyticsService.get_store_spending_analysis(
            self.user.id, 
            start_date=start_date, 
            end_date=end_date
        )
        
        # Should only include purchases within the date range
        self.assertIn('store_analysis', result)
        self.assertGreaterEqual(result['total_spending'], 0)
    
    def test_empty_data_handling(self):
        """Test analytics with no purchase data."""
        # Create a new user with no purchases
        empty_user = User(
            email='empty@example.com',
            name='Empty User',
            password_hash='hashed_password'
        )
        db.session.add(empty_user)
        db.session.commit()
        
        # Test all analytics methods with empty data
        monthly_result = AnalyticsService.get_monthly_spending(empty_user.id)
        self.assertEqual(len(monthly_result['monthly_spending']), 0)
        self.assertEqual(monthly_result['total_months'], 0)
        
        category_result = AnalyticsService.get_category_spending_analysis(empty_user.id)
        self.assertEqual(len(category_result['category_analysis']), 0)
        self.assertEqual(category_result['total_spending'], 0)
        
        store_result = AnalyticsService.get_store_spending_analysis(empty_user.id)
        self.assertEqual(len(store_result['store_analysis']), 0)
        self.assertEqual(store_result['total_spending'], 0)
        
        trends_result = AnalyticsService.get_spending_trends(empty_user.id)
        self.assertEqual(len(trends_result['trends_data']), 0)
        self.assertEqual(trends_result['statistics']['total_spending'], 0)

if __name__ == '__main__':
    unittest.main()