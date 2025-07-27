from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user
from datetime import datetime
import hmac
from app import db
from app.models.user import User
from app.models.connection import Connection

api_user_friends_bp = Blueprint('api_user_friends', __name__)

# CSRF Protection for API endpoints
def verify_csrf_token():
    """Verify CSRF token for state-changing operations."""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.get('_csrf_token')
        request_token = request.headers.get('X-CSRF-Token') or request.json.get('_csrf_token') if request.json else None
        
        if not token or not request_token or not hmac.compare_digest(token, request_token):
            return False
    return True

# User profile endpoints
@api_user_friends_bp.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    """API endpoint to get user profile."""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'created_at': current_user.created_at.isoformat(),
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'is_email_verified': current_user.is_email_verified,
                'is_active': current_user.is_active,
                'settings': current_user.settings or {}
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Get profile error: {str(e)}")
        return jsonify({'error': 'Failed to get user profile'}), 500

@api_user_friends_bp.route('/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """API endpoint to update user profile."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Name cannot be empty'}), 400
            current_user.name = name
        
        if 'profile_image' in data:
            current_user.profile_image = data['profile_image'] or 'default.jpg'
        
        if 'settings' in data:
            # Merge with existing settings
            current_settings = current_user.settings or {}
            current_settings.update(data['settings'])
            current_user.settings = current_settings
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'settings': current_user.settings or {}
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update profile error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

# Friends management endpoints
@api_user_friends_bp.route('/user/friends', methods=['GET'])
@login_required
def get_friends():
    """API endpoint to get user's friends."""
    try:
        # Get accepted connections where current user is either user or friend
        connections = db.session.query(Connection).filter(
            ((Connection.user_id == current_user.id) | (Connection.friend_id == current_user.id)) &
            (Connection.status == 'accepted')
        ).all()
        
        friends = []
        for conn in connections:
            # Get the friend (the other user in the connection)
            friend_id = conn.friend_id if conn.user_id == current_user.id else conn.user_id
            friend = User.query.get(friend_id)
            
            if friend:
                friends.append({
                    'id': friend.id,
                    'name': friend.name,
                    'email': friend.email,
                    'profile_image': friend.profile_image,
                    'connection_date': conn.updated_at.isoformat() if conn.updated_at else conn.created_at.isoformat(),
                    'is_active': friend.is_active
                })
        
        return jsonify({
            'friends': friends,
            'count': len(friends)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get friends error: {str(e)}")
        return jsonify({'error': 'Failed to get friends'}), 500

@api_user_friends_bp.route('/user/friends/search', methods=['GET'])
@login_required
def search_users():
    """API endpoint to search for users to add as friends."""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'users': []}), 200
        
        if len(query) < 2:
            return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
        # Search by name or email (partial match)
        users = User.query.filter(
            (User.name.ilike(f'%{query}%') | User.email.ilike(f'%{query}%')) &
            (User.id != current_user.id) &  # Exclude current user
            (User.is_active == True)
        ).limit(limit).all()
        
        # Get existing connections to filter out already connected users
        existing_connections = db.session.query(Connection.user_id, Connection.friend_id).filter(
            ((Connection.user_id == current_user.id) | (Connection.friend_id == current_user.id)) &
            (Connection.status.in_(['pending', 'accepted']))
        ).all()
        
        # Create set of connected user IDs
        connected_user_ids = set()
        for conn in existing_connections:
            if conn.user_id == current_user.id:
                connected_user_ids.add(conn.friend_id)
            else:
                connected_user_ids.add(conn.user_id)
        
        # Filter out already connected users
        available_users = []
        for user in users:
            if user.id not in connected_user_ids:
                available_users.append({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'profile_image': user.profile_image
                })
        
        return jsonify({
            'users': available_users,
            'count': len(available_users)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Search users error: {str(e)}")
        return jsonify({'error': 'Failed to search users'}), 500

@api_user_friends_bp.route('/user/friends/request', methods=['POST'])
@login_required
def send_friend_request():
    """API endpoint to send a friend request."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        friend_id = data.get('friend_id')
        
        if not friend_id:
            return jsonify({'error': 'Friend ID is required'}), 400
        
        if friend_id == current_user.id:
            return jsonify({'error': 'Cannot send friend request to yourself'}), 400
        
        # Check if friend exists and is active
        friend = User.query.get(friend_id)
        if not friend or not friend.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Check if connection already exists
        existing_connection = Connection.query.filter(
            ((Connection.user_id == current_user.id) & (Connection.friend_id == friend_id)) |
            ((Connection.user_id == friend_id) & (Connection.friend_id == current_user.id))
        ).first()
        
        if existing_connection:
            if existing_connection.status == 'accepted':
                return jsonify({'error': 'Already friends with this user'}), 400
            elif existing_connection.status == 'pending':
                return jsonify({'error': 'Friend request already sent'}), 400
            elif existing_connection.status == 'rejected':
                # Update existing rejected connection to pending
                existing_connection.status = 'pending'
                existing_connection.user_id = current_user.id
                existing_connection.friend_id = friend_id
                existing_connection.updated_at = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'message': 'Friend request sent successfully',
                    'connection': {
                        'id': existing_connection.id,
                        'friend': {
                            'id': friend.id,
                            'name': friend.name,
                            'email': friend.email,
                            'profile_image': friend.profile_image
                        },
                        'status': existing_connection.status,
                        'created_at': existing_connection.created_at.isoformat()
                    }
                }), 200
        
        # Create new friend request
        connection = Connection(
            user_id=current_user.id,
            friend_id=friend_id,
            status='pending'
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'message': 'Friend request sent successfully',
            'connection': {
                'id': connection.id,
                'friend': {
                    'id': friend.id,
                    'name': friend.name,
                    'email': friend.email,
                    'profile_image': friend.profile_image
                },
                'status': connection.status,
                'created_at': connection.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Send friend request error: {str(e)}")
        return jsonify({'error': 'Failed to send friend request'}), 500

@api_user_friends_bp.route('/user/friends/requests', methods=['GET'])
@login_required
def get_friend_requests():
    """API endpoint to get pending friend requests."""
    try:
        request_type = request.args.get('type', 'received')  # 'sent' or 'received'
        
        if request_type == 'sent':
            # Get requests sent by current user
            connections = Connection.query.filter_by(
                user_id=current_user.id,
                status='pending'
            ).all()
            
            requests = []
            for conn in connections:
                friend = User.query.get(conn.friend_id)
                if friend:
                    requests.append({
                        'id': conn.id,
                        'user': {
                            'id': friend.id,
                            'name': friend.name,
                            'email': friend.email,
                            'profile_image': friend.profile_image
                        },
                        'status': conn.status,
                        'created_at': conn.created_at.isoformat(),
                        'type': 'sent'
                    })
        else:
            # Get requests received by current user
            connections = Connection.query.filter_by(
                friend_id=current_user.id,
                status='pending'
            ).all()
            
            requests = []
            for conn in connections:
                user = User.query.get(conn.user_id)
                if user:
                    requests.append({
                        'id': conn.id,
                        'user': {
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'profile_image': user.profile_image
                        },
                        'status': conn.status,
                        'created_at': conn.created_at.isoformat(),
                        'type': 'received'
                    })
        
        return jsonify({
            'requests': requests,
            'count': len(requests)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get friend requests error: {str(e)}")
        return jsonify({'error': 'Failed to get friend requests'}), 500

@api_user_friends_bp.route('/user/friends/requests/<int:request_id>/accept', methods=['PUT'])
@login_required
def accept_friend_request(request_id):
    """API endpoint to accept a friend request."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # Find the connection request
        connection = Connection.query.get(request_id)
        
        if not connection:
            return jsonify({'error': 'Friend request not found'}), 404
        
        # Verify that current user is the recipient of the request
        if connection.friend_id != current_user.id:
            return jsonify({'error': 'Not authorized to accept this request'}), 403
        
        if connection.status != 'pending':
            return jsonify({'error': 'Request is not pending'}), 400
        
        # Accept the request
        connection.status = 'accepted'
        connection.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Get the friend user info
        friend = User.query.get(connection.user_id)
        
        return jsonify({
            'message': 'Friend request accepted successfully',
            'connection': {
                'id': connection.id,
                'friend': {
                    'id': friend.id,
                    'name': friend.name,
                    'email': friend.email,
                    'profile_image': friend.profile_image
                },
                'status': connection.status,
                'accepted_at': connection.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Accept friend request error: {str(e)}")
        return jsonify({'error': 'Failed to accept friend request'}), 500

@api_user_friends_bp.route('/user/friends/requests/<int:request_id>/reject', methods=['PUT'])
@login_required
def reject_friend_request(request_id):
    """API endpoint to reject a friend request."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # Find the connection request
        connection = Connection.query.get(request_id)
        
        if not connection:
            return jsonify({'error': 'Friend request not found'}), 404
        
        # Verify that current user is the recipient of the request
        if connection.friend_id != current_user.id:
            return jsonify({'error': 'Not authorized to reject this request'}), 403
        
        if connection.status != 'pending':
            return jsonify({'error': 'Request is not pending'}), 400
        
        # Reject the request
        connection.status = 'rejected'
        connection.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Friend request rejected successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reject friend request error: {str(e)}")
        return jsonify({'error': 'Failed to reject friend request'}), 500

@api_user_friends_bp.route('/user/friends/<int:friend_id>', methods=['DELETE'])
@login_required
def remove_friend(friend_id):
    """API endpoint to remove a friend."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # Find the connection
        connection = Connection.query.filter(
            ((Connection.user_id == current_user.id) & (Connection.friend_id == friend_id)) |
            ((Connection.user_id == friend_id) & (Connection.friend_id == current_user.id))
        ).filter(Connection.status == 'accepted').first()
        
        if not connection:
            return jsonify({'error': 'Friend connection not found'}), 404
        
        # Remove the connection
        db.session.delete(connection)
        db.session.commit()
        
        return jsonify({
            'message': 'Friend removed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Remove friend error: {str(e)}")
        return jsonify({'error': 'Failed to remove friend'}), 500

@api_user_friends_bp.route('/user/friends/suggestions', methods=['GET'])
@login_required
def get_friend_suggestions():
    """API endpoint to get friend suggestions."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get current user's friends
        current_friends_query = db.session.query(Connection).filter(
            ((Connection.user_id == current_user.id) | (Connection.friend_id == current_user.id)) &
            (Connection.status == 'accepted')
        )
        
        current_friend_ids = set()
        for conn in current_friends_query:
            friend_id = conn.friend_id if conn.user_id == current_user.id else conn.user_id
            current_friend_ids.add(friend_id)
        
        # Get pending connections to exclude
        pending_connections = db.session.query(Connection).filter(
            ((Connection.user_id == current_user.id) | (Connection.friend_id == current_user.id)) &
            (Connection.status == 'pending')
        )
        
        pending_user_ids = set()
        for conn in pending_connections:
            user_id = conn.friend_id if conn.user_id == current_user.id else conn.user_id
            pending_user_ids.add(user_id)
        
        # Combine excluded IDs
        excluded_ids = current_friend_ids.union(pending_user_ids)
        excluded_ids.add(current_user.id)  # Exclude current user
        
        # Simple suggestion algorithm: get active users not already connected
        suggested_users = User.query.filter(
            ~User.id.in_(excluded_ids) &
            (User.is_active == True)
        ).limit(limit).all()
        
        suggestions = []
        for user in suggested_users:
            # Calculate mutual friends count
            user_friends_query = db.session.query(Connection).filter(
                ((Connection.user_id == user.id) | (Connection.friend_id == user.id)) &
                (Connection.status == 'accepted')
            )
            
            user_friend_ids = set()
            for conn in user_friends_query:
                friend_id = conn.friend_id if conn.user_id == user.id else conn.user_id
                user_friend_ids.add(friend_id)
            
            mutual_friends_count = len(current_friend_ids.intersection(user_friend_ids))
            
            suggestions.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'profile_image': user.profile_image,
                'mutual_friends_count': mutual_friends_count,
                'reason': 'mutual_friends' if mutual_friends_count > 0 else 'new_user'
            })
        
        # Sort by mutual friends count (descending)
        suggestions.sort(key=lambda x: x['mutual_friends_count'], reverse=True)
        
        return jsonify({
            'suggestions': suggestions,
            'count': len(suggestions)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get friend suggestions error: {str(e)}")
        return jsonify({'error': 'Failed to get friend suggestions'}), 500

@api_user_friends_bp.route('/user/friends/<int:friend_id>/profile', methods=['GET'])
@login_required
def get_friend_profile(friend_id):
    """API endpoint to get a friend's profile."""
    try:
        # Check if users are friends
        connection = Connection.query.filter(
            ((Connection.user_id == current_user.id) & (Connection.friend_id == friend_id)) |
            ((Connection.user_id == friend_id) & (Connection.friend_id == current_user.id))
        ).filter(Connection.status == 'accepted').first()
        
        if not connection:
            return jsonify({'error': 'Not friends with this user'}), 403
        
        # Get friend's profile
        friend = User.query.get(friend_id)
        
        if not friend or not friend.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        return jsonify({
            'user': {
                'id': friend.id,
                'name': friend.name,
                'profile_image': friend.profile_image,
                'created_at': friend.created_at.isoformat(),
                'last_login': friend.last_login.isoformat() if friend.last_login else None,
                'connection_date': connection.updated_at.isoformat() if connection.updated_at else connection.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get friend profile error: {str(e)}")
        return jsonify({'error': 'Failed to get friend profile'}), 500