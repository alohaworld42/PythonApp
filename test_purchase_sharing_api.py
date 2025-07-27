#!/usr/bin/env python3
"""
Test suite for purchase and sharing API endpoints.
Tests purchase listing, sharing, feed generation, and social interactions.
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
from app.models.connection import Connection
from app.models.interaction import Interaction

class TestPurchaseSharingAPI:
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
        """Create test users, products, and purchases."""
        # Create users
        user1 = User(
            name='Test User 1',
            email='user1@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user1)
        
        user2 = User(
            name='Test User 2',
            email='user2@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user2)
        
        db.session.commit()
        
        # Create products
        product1 = Product(
            external_id='prod1',
            source='shopify',
            title='Test Product 1',
            description='A great test product',
            image_url='https://example.com/product1.jpg',
            price=Decimal('29.99'),
            currency='USD',
            category='Electronics'
        )
        db.session.add(product1)
        
        product2 = Product(
            external_id='prod2',
            source='woocommerce',
            title='Test Product 2',
            description='Another test product',
            image_url='https://example.com/product2.jpg',
            price=Decimal('49.99'),
            currency='USD',
            category='Clothing'
        )
        db.session.add(product2)
        
        db.session.commit()
        
        # Create purchases
        purchase1 = Purchase(
            user_id=user1.id,
            product_id=product1.id,
            purchase_date=datetime.utcnow() - timedelta(days=1),
            store_name='Test Store 1',
            order_id='ORDER123',
            is_shared=False
        )
        db.session.add(purchase1)
        
        purchase2 = Purchase(
            user_id=user1.id,
            product_id=product2.id,
            purchase_date=datetime.utcnow() - timedelta(days=2),
            store_name='Test Store 2',
            order_id='ORDER456',
            is_shared=True,
            share_comment='Love this product!'
        )
        db.session.add(purchase2)
        
        purchase3 = Purchase(
            user_id=user2.id,
            product_id=product1.id,
            purchase_date=datetime.utcnow() - timedelta(days=3),
            store_name='Test Store 1',
            order_id='ORDER789',
            is_shared=True,
            share_comment='Great purchase!'
        )
        db.session.add(purchase3)
        
        db.session.commit()
        
        # Create friendship between users
        connection = Connection(
            user_id=user1.id,
            friend_id=user2.id,
            status='accepted'
        )
        db.session.add(connection)
        db.session.commit()
        
        return {
            'users': [user1, user2],
            'products': [product1, product2],
            'purchases': [purchase1, purchase2, purchase3]
        }
        
    def test_get_purchases(self):
        """Test getting user's purchases."""
        print("Testing get purchases...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get all purchases
        response = self.client.get('/api/purchases')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'purchases' in data
        assert len(data['purchases']) == 2  # User1 has 2 purchases
        assert 'pagination' in data
        
        # Test get shared purchases only
        response = self.client.get('/api/purchases?shared_only=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['purchases']) == 1  # Only 1 shared purchase
        assert data['purchases'][0]['is_shared'] == True
        
        # Test filtering by category
        response = self.client.get('/api/purchases?category=Electronics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['purchases']) >= 1
        assert data['purchases'][0]['product']['category'] == 'Electronics'
        
        # Test sorting by price
        response = self.client.get('/api/purchases?sort_by=price&sort_order=asc')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['purchases']) >= 2
        # First item should have lower price
        assert data['purchases'][0]['product']['price'] <= data['purchases'][1]['product']['price']
        
        print("✓ Get purchases works correctly")
        
    def test_get_purchase_detail(self):
        """Test getting purchase details."""
        print("Testing get purchase detail...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][0].id  # User1's first purchase
        
        # Test get own purchase detail
        response = self.client.get(f'/api/purchases/{purchase_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'purchase' in data
        assert data['purchase']['id'] == purchase_id
        assert 'product' in data['purchase']
        assert 'owner' in data['purchase']
        assert 'interactions' in data['purchase']
        
        # Test get non-existent purchase
        response = self.client.get('/api/purchases/99999')
        assert response.status_code == 404
        
        print("✓ Get purchase detail works correctly")
        
    def test_share_unshare_purchase(self):
        """Test sharing and unsharing purchases."""
        print("Testing share/unshare purchase...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][0].id  # User1's first purchase (not shared)
        
        # Test share purchase
        share_data = {
            'comment': 'Sharing this awesome product!',
            '_csrf_token': csrf_token
        }
        
        response = self.client.put(f'/api/purchases/{purchase_id}/share',
                                 data=json.dumps(share_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Purchase shared successfully'
        assert data['purchase']['is_shared'] == True
        assert data['purchase']['share_comment'] == 'Sharing this awesome product!'
        
        # Test unshare purchase
        unshare_data = {'_csrf_token': csrf_token}
        response = self.client.put(f'/api/purchases/{purchase_id}/unshare',
                                 data=json.dumps(unshare_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Purchase unshared successfully'
        assert data['purchase']['is_shared'] == False
        assert data['purchase']['share_comment'] is None
        
        # Test share purchase without authorization
        other_purchase_id = test_data['purchases'][2].id  # User2's purchase
        response = self.client.put(f'/api/purchases/{other_purchase_id}/share',
                                 data=json.dumps(share_data),
                                 content_type='application/json')
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'Not authorized' in data['error']
        
        print("✓ Share/unshare purchase works correctly")
        
    def test_get_feed(self):
        """Test getting social feed."""
        print("Testing get feed...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get feed
        response = self.client.get('/api/feed')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'feed' in data
        assert 'pagination' in data
        assert len(data['feed']) >= 1  # Should see friend's shared purchase
        
        # Verify feed item structure
        feed_item = data['feed'][0]
        assert 'id' in feed_item
        assert 'user' in feed_item
        assert 'product' in feed_item
        assert 'interactions' in feed_item
        assert feed_item['user']['id'] == test_data['users'][1].id  # User2's purchase
        
        # Test filter by friend
        friend_id = test_data['users'][1].id
        response = self.client.get(f'/api/feed?friend_id={friend_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['feed']) >= 1
        assert data['feed'][0]['user']['id'] == friend_id
        
        # Test filter by category
        response = self.client.get('/api/feed?category=Electronics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if len(data['feed']) > 0:
            assert data['feed'][0]['product']['category'] == 'Electronics'
        
        print("✓ Get feed works correctly")
        
    def test_like_purchase(self):
        """Test liking and unliking purchases."""
        print("Testing like purchase...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][2].id  # User2's shared purchase
        
        # Test like purchase
        like_data = {'_csrf_token': csrf_token}
        response = self.client.post(f'/api/purchases/{purchase_id}/like',
                                  data=json.dumps(like_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['action'] == 'liked'
        assert data['liked'] == True
        assert data['likes_count'] == 1
        
        # Test unlike purchase
        response = self.client.post(f'/api/purchases/{purchase_id}/like',
                                  data=json.dumps(like_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['action'] == 'unliked'
        assert data['liked'] == False
        assert data['likes_count'] == 0
        
        print("✓ Like purchase works correctly")
        
    def test_comment_purchase(self):
        """Test commenting on purchases."""
        print("Testing comment purchase...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][2].id  # User2's shared purchase
        
        # Test add comment
        comment_data = {
            'content': 'Great choice! I love this product too.',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post(f'/api/purchases/{purchase_id}/comment',
                                  data=json.dumps(comment_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'comment' in data
        assert data['comment']['content'] == 'Great choice! I love this product too.'
        assert data['comment']['user']['id'] == test_data['users'][0].id
        
        # Test add empty comment
        empty_comment_data = {
            'content': '',
            '_csrf_token': csrf_token
        }
        
        response = self.client.post(f'/api/purchases/{purchase_id}/comment',
                                  data=json.dumps(empty_comment_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Comment cannot be empty' in data['error']
        
        # Test add too long comment
        long_comment_data = {
            'content': 'x' * 1001,  # Over 1000 character limit
            '_csrf_token': csrf_token
        }
        
        response = self.client.post(f'/api/purchases/{purchase_id}/comment',
                                  data=json.dumps(long_comment_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'too long' in data['error']
        
        print("✓ Comment purchase works correctly")
        
    def test_save_purchase(self):
        """Test saving and unsaving purchases."""
        print("Testing save purchase...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][2].id  # User2's shared purchase
        
        # Test save purchase
        save_data = {'_csrf_token': csrf_token}
        response = self.client.post(f'/api/purchases/{purchase_id}/save',
                                  data=json.dumps(save_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['action'] == 'saved'
        assert data['saved'] == True
        
        # Test unsave purchase
        response = self.client.post(f'/api/purchases/{purchase_id}/save',
                                  data=json.dumps(save_data),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['action'] == 'unsaved'
        assert data['saved'] == False
        
        print("✓ Save purchase works correctly")
        
    def test_get_saved_purchases(self):
        """Test getting saved purchases."""
        print("Testing get saved purchases...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        purchase_id = test_data['purchases'][2].id  # User2's shared purchase
        
        # First save a purchase
        save_data = {'_csrf_token': csrf_token}
        response = self.client.post(f'/api/purchases/{purchase_id}/save',
                                  data=json.dumps(save_data),
                                  content_type='application/json')
        assert response.status_code == 200
        
        # Test get saved purchases
        response = self.client.get('/api/saved')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'saved_purchases' in data
        assert 'pagination' in data
        assert len(data['saved_purchases']) >= 1
        
        # Verify saved purchase structure
        saved_item = data['saved_purchases'][0]
        assert 'id' in saved_item
        assert 'saved_at' in saved_item
        assert 'user' in saved_item
        assert 'product' in saved_item
        assert saved_item['id'] == purchase_id
        
        print("✓ Get saved purchases works correctly")
        
    def test_get_categories_and_stores(self):
        """Test getting purchase categories and stores."""
        print("Testing get categories and stores...")
        
        test_data = self.create_test_data()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get categories
        response = self.client.get('/api/purchases/categories')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'categories' in data
        assert 'count' in data
        assert len(data['categories']) >= 1
        assert 'Electronics' in data['categories'] or 'Clothing' in data['categories']
        
        # Test get stores
        response = self.client.get('/api/purchases/stores')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'stores' in data
        assert 'count' in data
        assert len(data['stores']) >= 1
        assert 'Test Store 1' in data['stores'] or 'Test Store 2' in data['stores']
        
        print("✓ Get categories and stores works correctly")
        
    def run_all_tests(self):
        """Run all purchase and sharing API tests."""
        print("=" * 60)
        print("RUNNING PURCHASE AND SHARING API TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_get_purchases()
            self.test_get_purchase_detail()
            self.test_share_unshare_purchase()
            self.test_get_feed()
            self.test_like_purchase()
            self.test_comment_purchase()
            self.test_save_purchase()
            self.test_get_saved_purchases()
            self.test_get_categories_and_stores()
            
            print("\n" + "=" * 60)
            print("✅ ALL PURCHASE AND SHARING API TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.teardown()

if __name__ == '__main__':
    tester = TestPurchaseSharingAPI()
    tester.run_all_tests()