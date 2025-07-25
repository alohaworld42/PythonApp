import pytest
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from datetime import datetime, timedelta
import json

class TestAnalyticsFrontend:
    """Test analytics frontend functionality."""
    
    @pytest.fixture
    def app(self):
        """Create test app."""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def user(self, app):
        """Create test user."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('password123')
            )
            db.session.add(user)
            db.session.commit()
            return user
    
    @pytest.fixture
    def sample_data(self, app, user):
        """Create sample purchase data."""
        with app.app_context():
            # Get user from current session
            current_user = User.query.get(user.id)
            
            # Create products
            products = []
            categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden']
            stores = ['Amazon', 'Best Buy', 'Target', 'Walmart']
            
            for i in range(20):
                product = Product(
                    external_id=f'prod_{i}',
                    source='shopify',
                    title=f'Product {i}',
                    description=f'Description for product {i}',
                    image_url=f'https://example.com/image_{i}.jpg',
                    price=50.0 + (i * 10),
                    currency='USD',
                    category=categories[i % len(categories)]
                )
                products.append(product)
                db.session.add(product)
            
            db.session.commit()
            
            # Create purchases
            for i, product in enumerate(products):
                purchase_date = datetime.now() - timedelta(days=i * 10)
                purchase = Purchase(
                    user_id=current_user.id,
                    product_id=product.id,
                    purchase_date=purchase_date,
                    store_name=stores[i % len(stores)],
                    order_id=f'order_{i}',
                    is_shared=i % 2 == 0  # Share every other item
                )
                db.session.add(purchase)
            
            db.session.commit()
    
    def test_analytics_page_loads(self, client, user, sample_data):
        """Test that analytics page loads correctly."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check that key elements are present
        assert b'Shopping Analytics' in response.data
        assert b'Time Period' in response.data
        assert b'Spending Trends' in response.data
        assert b'Spending by Category' in response.data
        assert b'Top Stores' in response.data
        assert b'Monthly Spending' in response.data
        assert b'Category Details' in response.data
        assert b'Store Details' in response.data
    
    def test_analytics_javascript_included(self, client, user, sample_data):
        """Test that analytics JavaScript is included."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check that Chart.js and analytics.js are included
        assert b'chart.js' in response.data
        assert b'analytics.js' in response.data
    
    def test_analytics_controls_present(self, client, user, sample_data):
        """Test that analytics controls are present."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for time period controls
        assert b'period-select' in response.data
        assert b'year-select' in response.data
        assert b'refresh-analytics' in response.data
        
        # Check for chart type toggles
        assert b'trends-chart-type' in response.data
        assert b'category-chart-type' in response.data
        assert b'store-chart-type' in response.data
        assert b'monthly-chart-type' in response.data
        
        # Check for fullscreen buttons
        assert b'trends-fullscreen' in response.data
        assert b'category-fullscreen' in response.data
        assert b'store-fullscreen' in response.data
        assert b'monthly-fullscreen' in response.data
        
        # Check for table controls
        assert b'category-table-toggle' in response.data
        assert b'category-export' in response.data
        assert b'store-table-toggle' in response.data
        assert b'store-export' in response.data
    
    def test_analytics_responsive_classes(self, client, user, sample_data):
        """Test that responsive CSS classes are present."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for responsive grid classes
        assert b'grid-cols-1' in response.data
        assert b'lg:grid-cols-2' in response.data
        assert b'xl:grid-cols-2' in response.data
        
        # Check for responsive padding/margin classes
        assert b'p-4 lg:p-6' in response.data
        assert b'gap-6 lg:gap-8' in response.data
        
        # Check for responsive text classes
        assert b'text-lg lg:text-xl' in response.data
        assert b'text-xs lg:text-sm' in response.data
        
        # Check for responsive table classes
        assert b'hidden sm:table-cell' in response.data
        assert b'px-3 lg:px-6' in response.data
    
    def test_analytics_chart_containers(self, client, user, sample_data):
        """Test that chart containers have proper responsive heights."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for responsive chart heights
        assert b'h-64 sm:h-72 lg:h-80' in response.data
        
        # Check for chart canvas elements
        assert b'spending-trends-chart' in response.data
        assert b'category-chart' in response.data
        assert b'store-chart' in response.data
        assert b'monthly-chart' in response.data
    
    def test_analytics_summary_cards(self, client, user, sample_data):
        """Test that summary cards are present and responsive."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for summary card elements
        assert b'total-spending' in response.data
        assert b'avg-monthly' in response.data
        assert b'total-purchases' in response.data
        assert b'spending-trend' in response.data
        
        # Check for responsive grid for summary cards
        assert b'grid-cols-1 md:grid-cols-2 lg:grid-cols-4' in response.data
    
    def test_analytics_loading_state(self, client, user, sample_data):
        """Test that loading state elements are present."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for loading state
        assert b'analytics-loading' in response.data
        assert b'Loading analytics data' in response.data
        assert b'animate-spin' in response.data
    
    def test_analytics_table_pagination(self, client, user, sample_data):
        """Test that table pagination elements are present."""
        # Login user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
        
        response = client.get('/user/analytics')
        assert response.status_code == 200
        
        # Check for pagination elements
        assert b'category-table-pagination' in response.data
        assert b'store-table-pagination' in response.data
        assert b'category-showing-start' in response.data
        assert b'category-showing-end' in response.data
        assert b'category-total' in response.data
        assert b'store-showing-start' in response.data
        assert b'store-showing-end' in response.data
        assert b'store-total' in response.data
        
        # Check for pagination buttons
        assert b'category-prev' in response.data
        assert b'category-next' in response.data
        assert b'store-prev' in response.data
        assert b'store-next' in response.data