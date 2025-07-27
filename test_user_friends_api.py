#!/usr/bin/env python3
"""
Test suite for user and friends API endpoints.
Tests profile management, friend search, friend requests, and friend management.
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from app.models.user import User
from app.models.connection import Connection

class TestUserFriendsAPI:
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
        
    def create_test_users(self):
        """Create test users for testing."""
        users = []
        
        # Create main test user
        user1 = User(
            name='Test User 1',
            email='user1@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user1)
        
        # Create additional test users
        user2 = User(
            name='Test User 2',
            email='user2@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user2)
        
        user3 = User(
            name='Test User 3',
            email='user3@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user3)
        
        user4 = User(
            name='John Doe',
            email='john@example.com',
            password_hash=User.hash_password('TestPassword123'),
            is_email_verified=True
        )
        db.session.add(user4)
        
        db.session.commit()
        
        return [user1, user2, user3, user4]
        
    def test_user_profile_management(self):
        """Test user profile get and update endpoints."""
        print("Testing user profile management...")
        
        users = self.create_test_users()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get profile
        response = self.client.get('/api/user/profile')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == 'user1@example.com'
        assert data['user']['name'] == 'Test User 1'
        
        # Test update profile
        update_data = {
            'name': 'Updated Test User 1',
            'profile_image': 'new_profile.jpg',
            'settings': {
                'theme': 'dark',
                'notifications': True
            },
            '_csrf_token': csrf_token
        }
        
        response = self.client.put('/api/user/profile',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Profile updated successfully'
        assert data['user']['name'] == 'Updated Test User 1'
        assert data['user']['profile_image'] == 'new_profile.jpg'
        assert data['user']['settings']['theme'] == 'dark'
        
        # Test update with empty name
        invalid_update_data = {
            'name': '',
            '_csrf_token': csrf_token
        }
        
        response = self.client.put('/api/user/profile',
                                 data=json.dumps(invalid_update_data),
                                 content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Name cannot be empty' in data['error']
        
        print("✓ User profile management works correctly")
        
    def test_user_search(self):
        """Test user search functionality."""
        print("Testing user search...")
        
        users = self.create_test_users()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test search by name
        response = self.client.get('/api/user/friends/search?q=Test User 2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) >= 1
        assert any(user['name'] == 'Test User 2' for user in data['users'])
        
        # Test search by email
        response = self.client.get('/api/user/friends/search?q=john@example.com')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['users']) >= 1
        assert any(user['email'] == 'john@example.com' for user in data['users'])
        
        # Test search with short query
        response = self.client.get('/api/user/friends/search?q=a')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'at least 2 characters' in data['error']
        
        # Test empty search
        response = self.client.get('/api/user/friends/search?q=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['users'] == []
        
        print("✓ User search works correctly")
        
    def test_friend_requests(self):
        """Test friend request functionality."""
        print("Testing friend requests...")
        
        users = self.create_test_users()
        csrf_token = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test send friend request
        request_data = {
            'friend_id': users[1].id,  # user2
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/user/friends/request',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Friend request sent successfully'
        assert data['connection']['friend']['id'] == users[1].id
        assert data['connection']['status'] == 'pending'
        
        # Test send duplicate friend request
        response = self.client.post('/api/user/friends/request',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already sent' in data['error']
        
        # Test send friend request to self
        self_request_data = {
            'friend_id': users[0].id,  # user1 (self)
            '_csrf_token': csrf_token
        }
        
        response = self.client.post('/api/user/friends/request',
                                  data=json.dumps(self_request_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Cannot send friend request to yourself' in data['error']
        
        # Test get sent friend requests
        response = self.client.get('/api/user/friends/requests?type=sent')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'requests' in data
        assert len(data['requests']) >= 1
        assert data['requests'][0]['type'] == 'sent'
        assert data['requests'][0]['user']['id'] == users[1].id
        
        print("✓ Friend requests work correctly")
        
    def test_friend_request_responses(self):
        """Test accepting and rejecting friend requests."""
        print("Testing friend request responses...")
        
        users = self.create_test_users()
        
        # User1 sends request to User2
        csrf_token1 = self.login_user('user1@example.com', 'TestPassword123')
        request_data = {
            'friend_id': users[1].id,
            '_csrf_token': csrf_token1
        }
        
        response = self.client.post('/api/user/friends/request',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        connection_id = json.loads(response.data)['connection']['id']
        
        # Logout user1 and login user2
        self.client.post('/api/auth/logout',
                        data=json.dumps({'_csrf_token': csrf_token1}),
                        content_type='application/json')
        
        csrf_token2 = self.login_user('user2@example.com', 'TestPassword123')
        
        # Test get received friend requests
        response = self.client.get('/api/user/friends/requests?type=received')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['requests']) >= 1
        assert data['requests'][0]['type'] == 'received'
        assert data['requests'][0]['user']['id'] == users[0].id
        
        # Test accept friend request
        accept_data = {'_csrf_token': csrf_token2}
        response = self.client.put(f'/api/user/friends/requests/{connection_id}/accept',
                                 data=json.dumps(accept_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Friend request accepted successfully'
        assert data['connection']['status'] == 'accepted'
        
        # Test get friends list
        response = self.client.get('/api/user/friends')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['friends']) >= 1
        assert data['friends'][0]['id'] == users[0].id
        
        print("✓ Friend request responses work correctly")
        
    def test_friend_rejection(self):
        """Test rejecting friend requests."""
        print("Testing friend rejection...")
        
        users = self.create_test_users()
        
        # User1 sends request to User3
        csrf_token1 = self.login_user('user1@example.com', 'TestPassword123')
        request_data = {
            'friend_id': users[2].id,  # user3
            '_csrf_token': csrf_token1
        }
        
        response = self.client.post('/api/user/friends/request',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        connection_id = json.loads(response.data)['connection']['id']
        
        # Logout user1 and login user3
        self.client.post('/api/auth/logout',
                        data=json.dumps({'_csrf_token': csrf_token1}),
                        content_type='application/json')
        
        csrf_token3 = self.login_user('user3@example.com', 'TestPassword123')
        
        # Test reject friend request
        reject_data = {'_csrf_token': csrf_token3}
        response = self.client.put(f'/api/user/friends/requests/{connection_id}/reject',
                                 data=json.dumps(reject_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Friend request rejected successfully'
        
        # Verify no friendship was created
        response = self.client.get('/api/user/friends')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['friends']) == 0
        
        print("✓ Friend rejection works correctly")
        
    def test_remove_friend(self):
        """Test removing friends."""
        print("Testing friend removal...")
        
        users = self.create_test_users()
        
        # Create a friendship between user1 and user4
        connection = Connection(
            user_id=users[0].id,
            friend_id=users[3].id,
            status='accepted'
        )
        db.session.add(connection)
        db.session.commit()
        
        csrf_token1 = self.login_user('user1@example.com', 'TestPassword123')
        
        # Verify friendship exists
        response = self.client.get('/api/user/friends')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['friends']) >= 1
        assert any(friend['id'] == users[3].id for friend in data['friends'])
        
        # Test remove friend
        remove_data = {'_csrf_token': csrf_token1}
        response = self.client.delete(f'/api/user/friends/{users[3].id}',
                                    data=json.dumps(remove_data),
                                    content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Friend removed successfully'
        
        # Verify friendship was removed
        response = self.client.get('/api/user/friends')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert not any(friend['id'] == users[3].id for friend in data['friends'])
        
        print("✓ Friend removal works correctly")
        
    def test_friend_suggestions(self):
        """Test friend suggestions."""
        print("Testing friend suggestions...")
        
        users = self.create_test_users()
        csrf_token1 = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get friend suggestions
        response = self.client.get('/api/user/friends/suggestions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'suggestions' in data
        assert len(data['suggestions']) >= 1
        
        # Verify current user is not in suggestions
        assert not any(suggestion['id'] == users[0].id for suggestion in data['suggestions'])
        
        # Test with limit
        response = self.client.get('/api/user/friends/suggestions?limit=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['suggestions']) <= 2
        
        print("✓ Friend suggestions work correctly")
        
    def test_friend_profile(self):
        """Test getting friend profile."""
        print("Testing friend profile...")
        
        users = self.create_test_users()
        
        # Create a friendship between user1 and user2
        connection = Connection(
            user_id=users[0].id,
            friend_id=users[1].id,
            status='accepted'
        )
        db.session.add(connection)
        db.session.commit()
        
        csrf_token1 = self.login_user('user1@example.com', 'TestPassword123')
        
        # Test get friend profile
        response = self.client.get(f'/api/user/friends/{users[1].id}/profile')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['id'] == users[1].id
        assert data['user']['name'] == 'Test User 2'
        assert 'connection_date' in data['user']
        
        # Test get profile of non-friend
        response = self.client.get(f'/api/user/friends/{users[2].id}/profile')
        assert response.status_code == 403
        
        data = json.loads(response.data)
        assert 'Not friends with this user' in data['error']
        
        print("✓ Friend profile works correctly")
        
    def run_all_tests(self):
        """Run all user and friends API tests."""
        print("=" * 60)
        print("RUNNING USER AND FRIENDS API TESTS")
        print("=" * 60)
        
        try:
            self.setup()
            
            self.test_user_profile_management()
            self.test_user_search()
            self.test_friend_requests()
            self.test_friend_request_responses()
            self.test_friend_rejection()
            self.test_remove_friend()
            self.test_friend_suggestions()
            self.test_friend_profile()
            
            print("\n" + "=" * 60)
            print("✅ ALL USER AND FRIENDS API TESTS PASSED!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            self.teardown()

if __name__ == '__main__':
    tester = TestUserFriendsAPI()
    tester.run_all_tests()