"""
Test configuration and fixtures for the BuyRoll application.
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.models.store_integration import StoreIntegration

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('config.TestingConfig')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User',
            password_hash=User.hash_password('testpassword'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        db.session.expunge(user)  # Detach from session
        
        # Return a fresh instance
        return User.query.get(user_id)

@pytest.fixture
def test_user2(app):
    """Create a second test user for friend testing."""
    with app.app_context():
        user = User(
            email='test2@example.com',
            name='Test User 2',
            password_hash=User.hash_password('testpassword2'),
            is_email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        db.session.expunge(user)  # Detach from session
        
        # Return a fresh instance
        return User.query.get(user_id)

@pytest.fixture
def test_products(app):
    """Create test products."""
    with app.app_context():
        products = [
            Product(
                title='Laptop',
                source='shopify',
                price=999.99,
                currency='USD',
                category='Electronics',
                external_id='laptop-001'
            ),
            Product(
                title='T-Shirt',
                source='woocommerce',
                price=29.99,
                currency='USD',
                category='Clothing',
                external_id='tshirt-001'
            ),
            Product(
                title='Coffee Maker',
                source='shopify',
                price=149.99,
                currency='USD',
                category='Home',
                external_id='coffee-001'
            )
        ]
        
        for product in products:
            db.session.add(product)
        db.session.commit()
        
        # Get IDs and return fresh instances
        product_ids = [p.id for p in products]
        for product in products:
            db.session.expunge(product)
        
        return [Product.query.get(pid) for pid in product_ids]

@pytest.fixture
def test_purchases(app, test_user, test_products):
    """Create test purchases."""
    with app.app_context():
        # Refresh objects in current session
        user = User.query.get(test_user.id)
        products = [Product.query.get(p.id) for p in test_products]
        
        now = datetime.now()
        purchases = [
            Purchase(
                user_id=user.id,
                product_id=products[0].id,
                purchase_date=now - timedelta(days=30),
                store_name='Tech Store',
                order_id='ORDER001',
                is_shared=True
            ),
            Purchase(
                user_id=user.id,
                product_id=products[1].id,
                purchase_date=now - timedelta(days=15),
                store_name='Fashion Store',
                order_id='ORDER002',
                is_shared=False
            ),
            Purchase(
                user_id=user.id,
                product_id=products[2].id,
                purchase_date=now - timedelta(days=5),
                store_name='Home Store',
                order_id='ORDER003',
                is_shared=True
            )
        ]
        
        for purchase in purchases:
            db.session.add(purchase)
        db.session.commit()
        
        # Get IDs and return fresh instances
        purchase_ids = [p.id for p in purchases]
        for purchase in purchases:
            db.session.expunge(purchase)
        
        return [Purchase.query.get(pid) for pid in purchase_ids]

@pytest.fixture
def test_connection(app, test_user, test_user2):
    """Create a test connection between users."""
    with app.app_context():
        # Refresh objects in current session
        user1 = User.query.get(test_user.id)
        user2 = User.query.get(test_user2.id)
        
        connection = Connection(
            user_id=user1.id,
            friend_id=user2.id,
            status='accepted'
        )
        db.session.add(connection)
        db.session.commit()
        connection_id = connection.id
        db.session.expunge(connection)
        
        return Connection.query.get(connection_id)

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated client session."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client