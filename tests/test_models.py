"""
Unit tests for database models.
"""
import pytest
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.models.store_integration import StoreIntegration

class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self, app):
        """Test user creation with required fields."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash='hashed_password'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.email == 'test@example.com'
            assert user.name == 'Test User'
            assert user.is_active is True
            assert user.is_email_verified is False
            assert user.created_at is not None
    
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            password = 'testpassword123'
            hashed = User.hash_password(password)
            
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=hashed
            )
            
            assert user.check_password(password) is True
            assert user.check_password('wrongpassword') is False
    
    def test_reset_token_generation(self, app):
        """Test password reset token generation and verification."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            token = user.get_reset_token()
            assert token is not None
            
            # Verify token
            verified_user = User.verify_reset_token(token)
            assert verified_user.id == user.id
            
            # Test invalid token
            invalid_user = User.verify_reset_token('invalid_token')
            assert invalid_user is None
    
    def test_email_verification(self, app):
        """Test email verification token generation and verification."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            token = user.generate_email_verification_token()
            assert token is not None
            assert user.email_verification_token == token
            
            # Verify email
            result = user.verify_email(token)
            assert result is True
            assert user.is_email_verified is True
            assert user.email_verification_token is None
            
            # Test invalid token
            user.is_email_verified = False
            user.generate_email_verification_token()
            result = user.verify_email('invalid_token')
            assert result is False
    
    def test_user_relationships(self, app):
        """Test user model relationships."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            # Test purchases relationship
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001'
            )
            db.session.add(purchase)
            db.session.commit()
            
            assert len(user.purchases) == 1
            assert user.purchases[0].store_name == 'Test Store'

class TestProductModel:
    """Test cases for the Product model."""
    
    def test_product_creation(self, app):
        """Test product creation with required fields."""
        with app.app_context():
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD',
                category='Electronics'
            )
            db.session.add(product)
            db.session.commit()
            
            assert product.id is not None
            assert product.title == 'Test Product'
            assert product.source == 'shopify'
            assert float(product.price) == 99.99
            assert product.currency == 'USD'
            assert product.category == 'Electronics'
    
    def test_product_with_metadata(self, app):
        """Test product creation with metadata."""
        with app.app_context():
            metadata = {
                'brand': 'Apple',
                'model': 'iPhone 13',
                'color': 'Blue'
            }
            
            product = Product(
                title='iPhone 13',
                source='shopify',
                price=799.99,
                currency='USD',
                category='Electronics',
                product_metadata=metadata
            )
            db.session.add(product)
            db.session.commit()
            
            assert product.product_metadata == metadata
            assert product.product_metadata['brand'] == 'Apple'
    
    def test_product_relationships(self, app):
        """Test product model relationships."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            # Create purchase for this product
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001'
            )
            db.session.add(purchase)
            db.session.commit()
            
            assert len(product.purchases) == 1
            assert product.purchases[0].user_id == user.id

class TestPurchaseModel:
    """Test cases for the Purchase model."""
    
    def test_purchase_creation(self, app):
        """Test purchase creation with required fields."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001'
            )
            db.session.add(purchase)
            db.session.commit()
            
            assert purchase.id is not None
            assert purchase.user_id == user.id
            assert purchase.product_id == product.id
            assert purchase.store_name == 'Test Store'
            assert purchase.order_id == 'ORDER001'
            assert purchase.is_shared is False
            assert purchase.created_at is not None
            assert purchase.updated_at is not None
    
    def test_purchase_sharing(self, app):
        """Test purchase sharing functionality."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001',
                is_shared=True,
                share_comment='Great product!'
            )
            db.session.add(purchase)
            db.session.commit()
            
            assert purchase.is_shared is True
            assert purchase.share_comment == 'Great product!'
    
    def test_purchase_date_handling(self, app):
        """Test purchase date handling."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            custom_date = datetime(2023, 6, 15, 10, 30, 0)
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001',
                purchase_date=custom_date
            )
            db.session.add(purchase)
            db.session.commit()
            
            assert purchase.purchase_date == custom_date

class TestConnectionModel:
    """Test cases for the Connection model."""
    
    def test_connection_creation(self, app):
        """Test connection creation between users."""
        with app.app_context():
            user1 = User(
                email='test1@example.com',
                name='Test User 1',
                password_hash=User.hash_password('testpassword')
            )
            user2 = User(
                email='test2@example.com',
                name='Test User 2',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            connection = Connection(
                user_id=user1.id,
                friend_id=user2.id,
                status='pending'
            )
            db.session.add(connection)
            db.session.commit()
            
            assert connection.id is not None
            assert connection.user_id == user1.id
            assert connection.friend_id == user2.id
            assert connection.status == 'pending'
            assert connection.created_at is not None
            assert connection.updated_at is not None
    
    def test_connection_status_updates(self, app):
        """Test connection status updates."""
        with app.app_context():
            user1 = User(
                email='test1@example.com',
                name='Test User 1',
                password_hash=User.hash_password('testpassword')
            )
            user2 = User(
                email='test2@example.com',
                name='Test User 2',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            connection = Connection(
                user_id=user1.id,
                friend_id=user2.id,
                status='pending'
            )
            db.session.add(connection)
            db.session.commit()
            
            original_updated_at = connection.updated_at
            
            # Update status
            connection.status = 'accepted'
            db.session.commit()
            
            assert connection.status == 'accepted'
            assert connection.updated_at > original_updated_at
    
    def test_connection_relationships(self, app):
        """Test connection model relationships."""
        with app.app_context():
            user1 = User(
                email='test1@example.com',
                name='Test User 1',
                password_hash=User.hash_password('testpassword')
            )
            user2 = User(
                email='test2@example.com',
                name='Test User 2',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            connection = Connection(
                user_id=user1.id,
                friend_id=user2.id,
                status='accepted'
            )
            db.session.add(connection)
            db.session.commit()
            
            # Test relationships
            assert len(user1.connections_initiated) == 1
            assert len(user2.connections_received) == 1
            assert user1.connections_initiated[0].friend_id == user2.id
            assert user2.connections_received[0].user_id == user1.id

class TestInteractionModel:
    """Test cases for the Interaction model."""
    
    def test_interaction_creation(self, app):
        """Test interaction creation."""
        with app.app_context():
            from app.models.interaction import Interaction
            
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001'
            )
            db.session.add(purchase)
            db.session.commit()
            
            interaction = Interaction(
                user_id=user.id,
                purchase_id=purchase.id,
                type='like'
            )
            db.session.add(interaction)
            db.session.commit()
            
            assert interaction.id is not None
            assert interaction.user_id == user.id
            assert interaction.purchase_id == purchase.id
            assert interaction.type == 'like'
            assert interaction.created_at is not None
    
    def test_interaction_with_content(self, app):
        """Test interaction with content (comment)."""
        with app.app_context():
            from app.models.interaction import Interaction
            
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            product = Product(
                title='Test Product',
                source='shopify',
                price=99.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER001'
            )
            db.session.add(purchase)
            db.session.commit()
            
            interaction = Interaction(
                user_id=user.id,
                purchase_id=purchase.id,
                type='comment',
                content='Great choice!'
            )
            db.session.add(interaction)
            db.session.commit()
            
            assert interaction.type == 'comment'
            assert interaction.content == 'Great choice!'

class TestStoreIntegrationModel:
    """Test cases for the StoreIntegration model."""
    
    def test_store_integration_creation(self, app):
        """Test store integration creation."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            integration = StoreIntegration(
                user_id=user.id,
                platform='shopify',
                store_url='https://mystore.myshopify.com',
                access_token='encrypted_token',
                metadata={'shop_name': 'My Store'}
            )
            db.session.add(integration)
            db.session.commit()
            
            assert integration.id is not None
            assert integration.user_id == user.id
            assert integration.platform == 'shopify'
            assert integration.store_url == 'https://mystore.myshopify.com'
            assert integration.access_token == 'encrypted_token'
            assert integration.metadata['shop_name'] == 'My Store'
            assert integration.created_at is not None
    
    def test_store_integration_sync_tracking(self, app):
        """Test store integration sync tracking."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            sync_time = datetime.now()
            
            integration = StoreIntegration(
                user_id=user.id,
                platform='woocommerce',
                store_url='https://mystore.com',
                access_token='encrypted_token',
                last_sync=sync_time
            )
            db.session.add(integration)
            db.session.commit()
            
            assert integration.last_sync == sync_time
    
    def test_store_integration_relationships(self, app):
        """Test store integration model relationships."""
        with app.app_context():
            user = User(
                email='test@example.com',
                name='Test User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            integration = StoreIntegration(
                user_id=user.id,
                platform='shopify',
                store_url='https://mystore.myshopify.com',
                access_token='encrypted_token'
            )
            db.session.add(integration)
            db.session.commit()
            
            assert len(user.store_integrations) == 1
            assert user.store_integrations[0].platform == 'shopify'