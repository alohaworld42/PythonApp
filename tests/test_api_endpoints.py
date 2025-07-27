"""
Unit tests for API endpoints.
"""
import pytest
import json
from flask import url_for
from app import db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection

class TestAuthAPI:
    """Test cases for authentication API endpoints."""
    
    def test_api_login_success(self, client, test_user):
        """Test successful API login."""
        response = client.post('/api/auth/login', 
            json={
                'email': test_user.email,
                'password': 'testpassword'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['email'] == test_user.email
    
    def test_api_login_invalid_credentials(self, client, test_user):
        """Test API login with invalid credentials."""
        response = client.post('/api/auth/login',
            json={
                'email': test_user.email,
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_register_success(self, client, app):
        """Test successful API registration."""
        response = client.post('/api/auth/register',
            json={
                'name': 'API User',
                'email': 'apiuser@example.com',
                'password': 'testpassword123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
        
        # Verify user was created
        with app.app_context():
            user = User.query.filter_by(email='apiuser@example.com').first()
            assert user is not None
            assert user.name == 'API User'
    
    def test_api_register_existing_email(self, client, test_user):
        """Test API registration with existing email."""
        response = client.post('/api/auth/register',
            json={
                'name': 'Another User',
                'email': test_user.email,
                'password': 'testpassword123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_api_logout(self, authenticated_client):
        """Test API logout."""
        response = authenticated_client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

class TestUserFriendsAPI:
    """Test cases for user friends API endpoints."""
    
    def test_get_friends_list(self, authenticated_client, test_user, test_user2, test_connection):
        """Test getting friends list."""
        response = authenticated_client.get('/api/user/friends')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'friends' in data
        assert len(data['friends']) >= 1
        
        # Check friend data structure
        friend = data['friends'][0]
        assert 'id' in friend
        assert 'name' in friend
        assert 'email' in friend
    
    def test_send_friend_request(self, authenticated_client, test_user2, app):
        """Test sending a friend request."""
        response = authenticated_client.post('/api/user/friends/request',
            json={'friend_id': test_user2.id},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify connection was created
        with app.app_context():
            connection = Connection.query.filter_by(
                friend_id=test_user2.id,
                status='pending'
            ).first()
            assert connection is not None
    
    def test_accept_friend_request(self, client, test_user, test_user2, app):
        """Test accepting a friend request."""
        with app.app_context():
            # Create pending connection
            connection = Connection(
                user_id=test_user2.id,
                friend_id=test_user.id,
                status='pending'
            )
            db.session.add(connection)
            db.session.commit()
            connection_id = connection.id
        
        # Login as test_user to accept the request
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True
        
        response = client.put(f'/api/user/friends/{connection_id}/accept')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify connection status was updated
        with app.app_context():
            connection = Connection.query.get(connection_id)
            assert connection.status == 'accepted'
    
    def test_reject_friend_request(self, client, test_user, test_user2, app):
        """Test rejecting a friend request."""
        with app.app_context():
            # Create pending connection
            connection = Connection(
                user_id=test_user2.id,
                friend_id=test_user.id,
                status='pending'
            )
            db.session.add(connection)
            db.session.commit()
            connection_id = connection.id
        
        # Login as test_user to reject the request
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
            sess['_fresh'] = True
        
        response = client.put(f'/api/user/friends/{connection_id}/reject')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify connection status was updated
        with app.app_context():
            connection = Connection.query.get(connection_id)
            assert connection.status == 'rejected'
    
    def test_remove_friend(self, authenticated_client, test_connection, app):
        """Test removing a friend."""
        response = authenticated_client.delete(f'/api/user/friends/{test_connection.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify connection was deleted
        with app.app_context():
            connection = Connection.query.get(test_connection.id)
            assert connection is None

class TestPurchaseSharingAPI:
    """Test cases for purchase sharing API endpoints."""
    
    def test_get_purchases(self, authenticated_client, test_purchases):
        """Test getting user's purchases."""
        response = authenticated_client.get('/api/purchases')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'purchases' in data
        assert len(data['purchases']) >= len(test_purchases)
        
        # Check purchase data structure
        purchase = data['purchases'][0]
        assert 'id' in purchase
        assert 'product' in purchase
        assert 'store_name' in purchase
        assert 'purchase_date' in purchase
        assert 'is_shared' in purchase
    
    def test_get_single_purchase(self, authenticated_client, test_purchases):
        """Test getting a single purchase."""
        purchase_id = test_purchases[0].id
        response = authenticated_client.get(f'/api/purchases/{purchase_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'purchase' in data
        assert data['purchase']['id'] == purchase_id
    
    def test_share_purchase(self, authenticated_client, test_purchases, app):
        """Test sharing a purchase."""
        purchase_id = test_purchases[1].id  # Use unshared purchase
        
        response = authenticated_client.put(f'/api/purchases/{purchase_id}/share',
            json={'share_comment': 'Great product!'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify purchase was shared
        with app.app_context():
            purchase = Purchase.query.get(purchase_id)
            assert purchase.is_shared is True
            assert purchase.share_comment == 'Great product!'
    
    def test_unshare_purchase(self, authenticated_client, test_purchases, app):
        """Test unsharing a purchase."""
        purchase_id = test_purchases[0].id  # Use shared purchase
        
        response = authenticated_client.put(f'/api/purchases/{purchase_id}/unshare')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify purchase was unshared
        with app.app_context():
            purchase = Purchase.query.get(purchase_id)
            assert purchase.is_shared is False
            assert purchase.share_comment is None
    
    def test_get_feed(self, authenticated_client, test_connection, test_purchases):
        """Test getting social feed."""
        response = authenticated_client.get('/api/feed')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'feed_items' in data
        
        # Should contain shared purchases from friends
        if data['feed_items']:
            item = data['feed_items'][0]
            assert 'purchase' in item
            assert 'user' in item
            assert 'interactions' in item
    
    def test_like_purchase(self, authenticated_client, test_purchases, app):
        """Test liking a purchase."""
        purchase_id = test_purchases[0].id
        
        response = authenticated_client.post(f'/api/feed/item/{purchase_id}/like')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify interaction was created
        with app.app_context():
            from app.models.interaction import Interaction
            interaction = Interaction.query.filter_by(
                purchase_id=purchase_id,
                type='like'
            ).first()
            assert interaction is not None
    
    def test_comment_on_purchase(self, authenticated_client, test_purchases, app):
        """Test commenting on a purchase."""
        purchase_id = test_purchases[0].id
        comment_text = 'Nice choice!'
        
        response = authenticated_client.post(f'/api/feed/item/{purchase_id}/comment',
            json={'content': comment_text},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify comment was created
        with app.app_context():
            from app.models.interaction import Interaction
            interaction = Interaction.query.filter_by(
                purchase_id=purchase_id,
                type='comment'
            ).first()
            assert interaction is not None
            assert interaction.content == comment_text

class TestAnalyticsAPI:
    """Test cases for analytics API endpoints."""
    
    def test_get_spending_analytics(self, authenticated_client, test_purchases):
        """Test getting spending analytics."""
        response = authenticated_client.get('/api/analytics/spending')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'monthly_spending' in data
        assert 'total_spending' in data
    
    def test_get_category_analytics(self, authenticated_client, test_purchases):
        """Test getting category analytics."""
        response = authenticated_client.get('/api/analytics/categories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'category_analysis' in data
        assert 'total_categories' in data
    
    def test_get_store_analytics(self, authenticated_client, test_purchases):
        """Test getting store analytics."""
        response = authenticated_client.get('/api/analytics/stores')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'store_analysis' in data
        assert 'total_stores' in data
    
    def test_get_trends_analytics(self, authenticated_client, test_purchases):
        """Test getting trends analytics."""
        response = authenticated_client.get('/api/analytics/trends')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'trends_data' in data
        assert 'statistics' in data

class TestAPIErrorHandling:
    """Test cases for API error handling."""
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints."""
        endpoints = [
            '/api/user/friends',
            '/api/purchases',
            '/api/feed',
            '/api/analytics/spending'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_invalid_json_request(self, authenticated_client):
        """Test handling of invalid JSON requests."""
        response = authenticated_client.post('/api/user/friends/request',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_missing_required_fields(self, authenticated_client):
        """Test handling of missing required fields."""
        response = authenticated_client.post('/api/user/friends/request',
            json={},  # Missing friend_id
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_nonexistent_resource(self, authenticated_client):
        """Test accessing non-existent resources."""
        response = authenticated_client.get('/api/purchases/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_method_not_allowed(self, authenticated_client):
        """Test method not allowed errors."""
        response = authenticated_client.delete('/api/auth/login')
        
        assert response.status_code == 405