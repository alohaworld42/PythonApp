"""
Integration tests for the BuyRoll application.
Tests the interaction between different components and services.
"""
import pytest
import json
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.services.analytics_service import AnalyticsService
from app.services.purchase_sharing_service import PurchaseSharingService

class TestEcommerceIntegration:
    """Test e-commerce integration functionality."""
    
    def test_shopify_data_sync_flow(self, app):
        """Test complete Shopify data synchronization flow."""
        with app.app_context():
            # Create user
            user = User(
                email='shopify@example.com',
                name='Shopify User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Simulate Shopify product import
            shopify_product = Product(
                external_id='shopify_123',
                source='shopify',
                title='Shopify Product',
                price=99.99,
                currency='USD',
                category='Electronics'
            )
            db.session.add(shopify_product)
            db.session.commit()
            
            # Simulate purchase creation from Shopify order
            purchase = Purchase(
                user_id=user.id,
                product_id=shopify_product.id,
                store_name='My Shopify Store',
                order_id='shopify_order_123',
                purchase_date=datetime.now() - timedelta(days=1)
            )
            db.session.add(purchase)
            db.session.commit()
            
            # Verify integration
            assert purchase.product.source == 'shopify'
            assert purchase.product.external_id == 'shopify_123'
            assert purchase.user.email == 'shopify@example.com'
            assert len(user.purchases) == 1
    
    def test_woocommerce_data_sync_flow(self, app):
        """Test complete WooCommerce data synchronization flow."""
        with app.app_context():
            # Create user
            user = User(
                email='woo@example.com',
                name='WooCommerce User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Simulate WooCommerce product import
            woo_product = Product(
                external_id='woo_456',
                source='woocommerce',
                title='WooCommerce Product',
                price=149.99,
                currency='USD',
                category='Clothing'
            )
            db.session.add(woo_product)
            db.session.commit()
            
            # Simulate purchase creation from WooCommerce order
            purchase = Purchase(
                user_id=user.id,
                product_id=woo_product.id,
                store_name='My WooCommerce Store',
                order_id='woo_order_456',
                purchase_date=datetime.now() - timedelta(days=2)
            )
            db.session.add(purchase)
            db.session.commit()
            
            # Verify integration
            assert purchase.product.source == 'woocommerce'
            assert purchase.product.external_id == 'woo_456'
            assert purchase.user.email == 'woo@example.com'
            assert len(user.purchases) == 1
    
    def test_multi_platform_user_integration(self, app):
        """Test user with purchases from multiple e-commerce platforms."""
        with app.app_context():
            # Create user
            user = User(
                email='multi@example.com',
                name='Multi Platform User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Create products from different platforms
            shopify_product = Product(
                external_id='shopify_789',
                source='shopify',
                title='Shopify Item',
                price=79.99,
                currency='USD',
                category='Home'
            )
            
            woo_product = Product(
                external_id='woo_789',
                source='woocommerce',
                title='WooCommerce Item',
                price=129.99,
                currency='USD',
                category='Electronics'
            )
            
            db.session.add(shopify_product)
            db.session.add(woo_product)
            db.session.commit()
            
            # Create purchases from both platforms
            shopify_purchase = Purchase(
                user_id=user.id,
                product_id=shopify_product.id,
                store_name='Shopify Store',
                order_id='shopify_789'
            )
            
            woo_purchase = Purchase(
                user_id=user.id,
                product_id=woo_product.id,
                store_name='WooCommerce Store',
                order_id='woo_789'
            )
            
            db.session.add(shopify_purchase)
            db.session.add(woo_purchase)
            db.session.commit()
            
            # Verify multi-platform integration
            assert len(user.purchases) == 2
            sources = [p.product.source for p in user.purchases]
            assert 'shopify' in sources
            assert 'woocommerce' in sources

class TestSocialFeatureIntegration:
    """Test social feature integration."""
    
    def test_friend_connection_and_sharing_flow(self, app):
        """Test complete friend connection and purchase sharing flow."""
        with app.app_context():
            # Create two users
            user1 = User(
                email='user1@example.com',
                name='User One',
                password_hash=User.hash_password('testpassword')
            )
            user2 = User(
                email='user2@example.com',
                name='User Two',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            
            # Create connection between users
            connection = Connection(
                user_id=user1.id,
                friend_id=user2.id,
                status='accepted'
            )
            db.session.add(connection)
            db.session.commit()
            
            # Create product and purchase for user1
            product = Product(
                title='Shared Product',
                source='shopify',
                price=199.99,
                currency='USD',
                category='Electronics'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user1.id,
                product_id=product.id,
                store_name='Test Store',
                order_id='ORDER123',
                is_shared=True,
                share_comment='Great product!'
            )
            db.session.add(purchase)
            db.session.commit()
            
            # Create interaction from user2 on user1's purchase
            interaction = Interaction(
                user_id=user2.id,
                purchase_id=purchase.id,
                type='like'
            )
            db.session.add(interaction)
            db.session.commit()
            
            # Verify social integration
            assert connection.status == 'accepted'
            assert purchase.is_shared is True
            assert purchase.share_comment == 'Great product!'
            assert len(purchase.interactions) == 1
            assert purchase.interactions[0].type == 'like'
            assert purchase.interactions[0].user_id == user2.id
    
    def test_purchase_sharing_service_integration(self, app):
        """Test purchase sharing service integration."""
        with app.app_context():
            # Create users and connection
            user1 = User(
                email='sharer@example.com',
                name='Sharer',
                password_hash=User.hash_password('testpassword')
            )
            user2 = User(
                email='viewer@example.com',
                name='Viewer',
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
            
            # Create product and purchase
            product = Product(
                title='Service Test Product',
                source='shopify',
                price=299.99,
                currency='USD'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user1.id,
                product_id=product.id,
                store_name='Service Store',
                order_id='SERVICE123',
                is_shared=True
            )
            db.session.add(purchase)
            db.session.commit()
            
            # Test sharing service functionality
            shared_purchases = PurchaseSharingService.get_shared_purchases_for_user(user2.id)
            
            # Verify service integration
            assert len(shared_purchases) >= 1
            found_purchase = False
            for shared_purchase in shared_purchases:
                if shared_purchase['purchase']['id'] == purchase.id:
                    found_purchase = True
                    assert shared_purchase['user']['id'] == user1.id
                    assert shared_purchase['purchase']['is_shared'] is True
            
            assert found_purchase is True
    
    def test_social_feed_generation(self, app):
        """Test social feed generation with multiple users and purchases."""
        with app.app_context():
            # Create multiple users
            users = []
            for i in range(3):
                user = User(
                    email=f'user{i}@example.com',
                    name=f'User {i}',
                    password_hash=User.hash_password('testpassword')
                )
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            # Create connections (user 0 is friends with users 1 and 2)
            for i in range(1, 3):
                connection = Connection(
                    user_id=users[0].id,
                    friend_id=users[i].id,
                    status='accepted'
                )
                db.session.add(connection)
            db.session.commit()
            
            # Create products and shared purchases for friends
            for i in range(1, 3):
                product = Product(
                    title=f'Product {i}',
                    source='shopify',
                    price=100.00 * i,
                    currency='USD'
                )
                db.session.add(product)
                db.session.commit()
                
                purchase = Purchase(
                    user_id=users[i].id,
                    product_id=product.id,
                    store_name=f'Store {i}',
                    order_id=f'ORDER{i}',
                    is_shared=True,
                    share_comment=f'Comment {i}'
                )
                db.session.add(purchase)
            db.session.commit()
            
            # Generate feed for user 0
            feed = PurchaseSharingService.get_shared_purchases_for_user(users[0].id)
            
            # Verify feed integration
            assert len(feed) >= 2
            user_ids_in_feed = [item['user']['id'] for item in feed]
            assert users[1].id in user_ids_in_feed
            assert users[2].id in user_ids_in_feed

class TestAnalyticsIntegration:
    """Test analytics service integration."""
    
    def test_analytics_with_real_purchase_data(self, app):
        """Test analytics service with real purchase data."""
        with app.app_context():
            # Create user
            user = User(
                email='analytics@example.com',
                name='Analytics User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Create products in different categories
            products = [
                Product(title='Laptop', source='shopify', price=999.99, currency='USD', category='Electronics'),
                Product(title='T-Shirt', source='woocommerce', price=29.99, currency='USD', category='Clothing'),
                Product(title='Coffee Maker', source='shopify', price=149.99, currency='USD', category='Home'),
                Product(title='Phone', source='shopify', price=799.99, currency='USD', category='Electronics'),
            ]
            
            for product in products:
                db.session.add(product)
            db.session.commit()
            
            # Create purchases with different dates and stores
            now = datetime.now()
            purchases = [
                Purchase(
                    user_id=user.id,
                    product_id=products[0].id,
                    store_name='Tech Store',
                    order_id='TECH001',
                    purchase_date=now - timedelta(days=30)
                ),
                Purchase(
                    user_id=user.id,
                    product_id=products[1].id,
                    store_name='Fashion Store',
                    order_id='FASHION001',
                    purchase_date=now - timedelta(days=15)
                ),
                Purchase(
                    user_id=user.id,
                    product_id=products[2].id,
                    store_name='Home Store',
                    order_id='HOME001',
                    purchase_date=now - timedelta(days=5)
                ),
                Purchase(
                    user_id=user.id,
                    product_id=products[3].id,
                    store_name='Tech Store',
                    order_id='TECH002',
                    purchase_date=now - timedelta(days=10)
                ),
            ]
            
            for purchase in purchases:
                db.session.add(purchase)
            db.session.commit()
            
            # Test analytics integration
            monthly_spending = AnalyticsService.get_monthly_spending(user.id)
            category_analysis = AnalyticsService.get_category_spending_analysis(user.id)
            store_analysis = AnalyticsService.get_store_spending_analysis(user.id)
            
            # Verify analytics integration
            assert monthly_spending['total_months'] > 0
            assert len(monthly_spending['monthly_spending']) > 0
            
            assert len(category_analysis['category_analysis']) == 3  # Electronics, Clothing, Home
            categories = [item['category'] for item in category_analysis['category_analysis']]
            assert 'Electronics' in categories
            assert 'Clothing' in categories
            assert 'Home' in categories
            
            assert len(store_analysis['store_analysis']) == 3  # Tech Store, Fashion Store, Home Store
            stores = [item['store_name'] for item in store_analysis['store_analysis']]
            assert 'Tech Store' in stores
            assert 'Fashion Store' in stores
            assert 'Home Store' in stores
            
            # Tech Store should have highest spending (Laptop + Phone)
            tech_store_data = next(
                item for item in store_analysis['store_analysis'] 
                if item['store_name'] == 'Tech Store'
            )
            expected_tech_spending = 999.99 + 799.99
            assert abs(tech_store_data['total_spending'] - expected_tech_spending) < 0.01
    
    def test_comprehensive_analytics_integration(self, app):
        """Test comprehensive analytics integration."""
        with app.app_context():
            # Create user with diverse purchase history
            user = User(
                email='comprehensive@example.com',
                name='Comprehensive User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Create products and purchases spanning multiple months
            base_date = datetime(2023, 1, 1)
            for month in range(1, 7):  # 6 months of data
                for item in range(2):  # 2 items per month
                    product = Product(
                        title=f'Product M{month}I{item}',
                        source='shopify',
                        price=50.00 + (month * 10) + (item * 5),
                        currency='USD',
                        category='Electronics' if item == 0 else 'Clothing'
                    )
                    db.session.add(product)
                    db.session.commit()
                    
                    purchase = Purchase(
                        user_id=user.id,
                        product_id=product.id,
                        store_name=f'Store {month}',
                        order_id=f'ORDER_M{month}I{item}',
                        purchase_date=base_date.replace(month=month, day=15)
                    )
                    db.session.add(purchase)
            db.session.commit()
            
            # Test comprehensive analytics
            comprehensive = AnalyticsService.get_comprehensive_analytics(user.id)
            
            # Verify comprehensive integration
            assert 'monthly_spending' in comprehensive
            assert 'category_analysis' in comprehensive
            assert 'store_analysis' in comprehensive
            assert 'spending_trends' in comprehensive
            
            # Should have 6 months of data
            assert comprehensive['monthly_spending']['total_months'] == 6
            
            # Should have 2 categories
            assert len(comprehensive['category_analysis']['category_analysis']) == 2
            
            # Should have 6 different stores
            assert len(comprehensive['store_analysis']['store_analysis']) == 6

class TestEndToEndUserFlows:
    """Test complete end-to-end user flows."""
    
    def test_new_user_complete_flow(self, app):
        """Test complete flow for a new user."""
        with app.app_context():
            # 1. User registration
            user = User(
                email='newuser@example.com',
                name='New User',
                password_hash=User.hash_password('testpassword'),
                is_email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            # 2. E-commerce data import (simulated)
            product = Product(
                external_id='import_123',
                source='shopify',
                title='Imported Product',
                price=199.99,
                currency='USD',
                category='Electronics'
            )
            db.session.add(product)
            db.session.commit()
            
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                store_name='Imported Store',
                order_id='IMPORT123',
                purchase_date=datetime.now() - timedelta(days=7)
            )
            db.session.add(purchase)
            db.session.commit()
            
            # 3. Friend connection
            friend = User(
                email='friend@example.com',
                name='Friend User',
                password_hash=User.hash_password('testpassword'),
                is_email_verified=True
            )
            db.session.add(friend)
            db.session.commit()
            
            connection = Connection(
                user_id=user.id,
                friend_id=friend.id,
                status='accepted'
            )
            db.session.add(connection)
            db.session.commit()
            
            # 4. Purchase sharing
            purchase.is_shared = True
            purchase.share_comment = 'Love this product!'
            db.session.commit()
            
            # 5. Friend interaction
            interaction = Interaction(
                user_id=friend.id,
                purchase_id=purchase.id,
                type='like'
            )
            db.session.add(interaction)
            db.session.commit()
            
            # 6. Analytics generation
            analytics = AnalyticsService.get_comprehensive_analytics(user.id)
            
            # Verify complete flow
            assert user.is_email_verified is True
            assert len(user.purchases) == 1
            assert len(user.connections_initiated) == 1
            assert user.connections_initiated[0].status == 'accepted'
            assert purchase.is_shared is True
            assert len(purchase.interactions) == 1
            assert purchase.interactions[0].type == 'like'
            assert analytics['monthly_spending']['total_months'] > 0
    
    def test_social_shopping_discovery_flow(self, app):
        """Test social shopping discovery flow."""
        with app.app_context():
            # Create multiple users with different shopping patterns
            users = []
            for i in range(3):
                user = User(
                    email=f'shopper{i}@example.com',
                    name=f'Shopper {i}',
                    password_hash=User.hash_password('testpassword')
                )
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            # Create friend connections
            for i in range(1, 3):
                connection = Connection(
                    user_id=users[0].id,
                    friend_id=users[i].id,
                    status='accepted'
                )
                db.session.add(connection)
            db.session.commit()
            
            # Create diverse products and purchases
            categories = ['Electronics', 'Clothing', 'Home', 'Books']
            for i, user in enumerate(users[1:], 1):  # Skip first user
                for j, category in enumerate(categories):
                    product = Product(
                        title=f'{category} Item {i}{j}',
                        source='shopify',
                        price=50.00 + (i * 20) + (j * 10),
                        currency='USD',
                        category=category
                    )
                    db.session.add(product)
                    db.session.commit()
                    
                    purchase = Purchase(
                        user_id=user.id,
                        product_id=product.id,
                        store_name=f'Store {category}',
                        order_id=f'ORDER_{i}{j}',
                        is_shared=True,
                        share_comment=f'Great {category.lower()} item!'
                    )
                    db.session.add(purchase)
            db.session.commit()
            
            # User 0 discovers and interacts with friends' purchases
            shared_purchases = PurchaseSharingService.get_shared_purchases_for_user(users[0].id)
            
            # Simulate interactions
            interaction_count = 0
            for shared_purchase in shared_purchases[:3]:  # Interact with first 3
                interaction = Interaction(
                    user_id=users[0].id,
                    purchase_id=shared_purchase['purchase']['id'],
                    type='like' if interaction_count % 2 == 0 else 'save'
                )
                db.session.add(interaction)
                interaction_count += 1
            db.session.commit()
            
            # Verify discovery flow
            assert len(shared_purchases) >= 6  # 2 friends × 4 categories each
            
            # Check that interactions were created
            total_interactions = Interaction.query.filter_by(user_id=users[0].id).count()
            assert total_interactions == 3
            
            # Verify different interaction types
            like_interactions = Interaction.query.filter_by(
                user_id=users[0].id, 
                type='like'
            ).count()
            save_interactions = Interaction.query.filter_by(
                user_id=users[0].id, 
                type='save'
            ).count()
            
            assert like_interactions >= 1
            assert save_interactions >= 1

class TestAPIIntegration:
    """Test API integration with services."""
    
    def test_api_and_service_integration(self, app):
        """Test integration between API endpoints and services."""
        with app.app_context():
            # Create test data
            user = User(
                email='api@example.com',
                name='API User',
                password_hash=User.hash_password('testpassword')
            )
            db.session.add(user)
            db.session.commit()
            
            # Create products and purchases
            for i in range(3):
                product = Product(
                    title=f'API Product {i}',
                    source='shopify',
                    price=100.00 + (i * 50),
                    currency='USD',
                    category='Electronics'
                )
                db.session.add(product)
                db.session.commit()
                
                purchase = Purchase(
                    user_id=user.id,
                    product_id=product.id,
                    store_name=f'API Store {i}',
                    order_id=f'API_ORDER_{i}',
                    is_shared=i % 2 == 0  # Share every other purchase
                )
                db.session.add(purchase)
            db.session.commit()
            
            # Test service integration
            analytics = AnalyticsService.get_comprehensive_analytics(user.id)
            shared_purchases = PurchaseSharingService.get_shared_purchases_for_user(user.id)
            
            # Verify API-service integration
            assert analytics['monthly_spending']['total_months'] > 0
            assert analytics['category_analysis']['total_spending'] == 300.00  # 100 + 150 + 50
            
            # Should have shared purchases (even indices: 0, 2)
            user_shared_count = Purchase.query.filter_by(
                user_id=user.id, 
                is_shared=True
            ).count()
            assert user_shared_count == 2