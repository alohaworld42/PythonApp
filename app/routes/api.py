from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user, login_user, logout_user
from datetime import datetime, timedelta
import secrets
import re
import hmac
from app import db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.models.store_integration import StoreIntegration
from app.models.notification import Notification
from app.integrations.shopify import ShopifyClient
from app.integrations.woocommerce import WooCommerceClient
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService

api_bp = Blueprint('api', __name__)

# CSRF Protection for API endpoints
def verify_csrf_token():
    """Verify CSRF token for state-changing operations."""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.get('_csrf_token')
        request_token = request.headers.get('X-CSRF-Token') or request.json.get('_csrf_token') if request.json else None
        
        if not token or not request_token or not hmac.compare_digest(token, request_token):
            return False
    return True

# Helper functions for authentication
def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'$'$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

# Authentication endpoints
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for user registration."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=email,
            name=name,
            password_hash=User.hash_password(password),
            is_email_verified=True  # Auto-verify for now
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate CSRF token for the session
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token']
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """API endpoint for user login."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            # Add small delay to prevent timing attacks
            import time
            time.sleep(0.5)
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        if not user.is_email_verified:
            return jsonify({'error': 'Email not verified. Please check your email for verification link.'}), 401
        
        # Set session duration based on remember option
        if remember:
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
        
        # Log user in
        login_user(user, remember=remember)
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate CSRF token
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_image': user.profile_image,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """API endpoint for user logout."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        logout_user()
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@api_bp.route('/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """API endpoint to get current authenticated user."""
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'created_at': current_user.created_at.isoformat(),
                'is_email_verified': current_user.is_email_verified
            }
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get user info'}), 500

@api_bp.route('/auth/reset-password', methods=['POST'])
def request_password_reset():
    """API endpoint to request password reset."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = user.get_reset_token()
            # In a real implementation, you would send an email here
            # For now, we'll log the token for testing purposes
            current_app.logger.info(f"Password reset token for {email}: {reset_token}")
        
        # Always return success to prevent user enumeration
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'error': 'Password reset request failed'}), 500

@api_bp.route('/auth/reset-password/<token>', methods=['POST'])
def reset_password_with_token(token):
    """API endpoint to reset password with token."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verify token and get user
        user = User.verify_reset_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 400
        
        # Update password
        user.password_hash = User.hash_password(password)
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@api_bp.route('/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """API endpoint to change password for authenticated user."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not current_user.check_password(current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if new password is different from current
        if current_user.check_password(new_password):
            return jsonify({'error': 'New password must be different from current password'}), 400
        
        # Update password
        current_user.password_hash = User.hash_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500

@api_bp.route('/auth/social-login', methods=['POST'])
def social_login():
    """API endpoint for social login with OAuth providers."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        provider = data.get('provider')  # 'google', 'facebook', 'amazon'
        access_token = data.get('access_token')
        user_info = data.get('user_info', {})
        
        if not provider or not access_token:
            return jsonify({'error': 'Provider and access token are required'}), 400
        
        if provider not in ['google', 'facebook', 'amazon']:
            return jsonify({'error': 'Unsupported provider'}), 400
        
        # Extract user information from the social provider
        email = user_info.get('email', '').strip().lower()
        name = user_info.get('name', '').strip()
        profile_image = user_info.get('picture') or user_info.get('profile_image')
        
        if not email or not name:
            return jsonify({'error': 'Email and name are required from social provider'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format from social provider'}), 400
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # User exists, log them in
            if not user.is_active:
                return jsonify({'error': 'Account is deactivated'}), 401
            
            # Update profile information if needed
            if user.name != name:
                user.name = name
            if profile_image and user.profile_image == 'default.jpg':
                user.profile_image = profile_image
            
            user.last_login = datetime.utcnow()
            user.is_email_verified = True  # Social accounts are pre-verified
            db.session.commit()
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                password_hash=User.hash_password(secrets.token_urlsafe(32)),  # Random password
                profile_image=profile_image or 'default.jpg',
                is_email_verified=True,  # Social accounts are pre-verified
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
        
        # Log user in
        login_user(user, remember=True)  # Remember social logins
        
        # Generate CSRF token
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Social login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_image': user.profile_image,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_email_verified': user.is_email_verified
            },
            'csrf_token': session['_csrf_token'],
            'is_new_user': user.created_at > datetime.utcnow() - timedelta(minutes=1)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Social login error: {str(e)}")
        return jsonify({'error': 'Social login failed'}), 500

@api_bp.route('/auth/session', methods=['GET'])
def check_session():
    """API endpoint to check session status."""
    try:
        if current_user.is_authenticated:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'name': current_user.name,
                    'profile_image': current_user.profile_image,
                    'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                    'is_email_verified': current_user.is_email_verified
                },
                'csrf_token': session.get('_csrf_token')
            }), 200
        else:
            return jsonify({'authenticated': False}), 200
    except Exception as e:
        current_app.logger.error(f"Session check error: {str(e)}")
        return jsonify({'error': 'Session check failed'}), 500

@api_bp.route('/auth/refresh-session', methods=['POST'])
@login_required
def refresh_session():
    """API endpoint to refresh user session."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # Update last activity
        current_user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate new CSRF token
        session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'message': 'Session refreshed successfully',
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'profile_image': current_user.profile_image,
                'last_login': current_user.last_login.isoformat()
            },
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Session refresh error: {str(e)}")
        return jsonify({'error': 'Session refresh failed'}), 500

@api_bp.route('/auth/csrf-token', methods=['GET'])
def get_csrf_token():
    """API endpoint to get CSRF token."""
    try:
        if '_csrf_token' not in session:
            session['_csrf_token'] = secrets.token_hex(16)
        
        return jsonify({
            'csrf_token': session['_csrf_token']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"CSRF token error: {str(e)}")
        return jsonify({'error': 'Failed to get CSRF token'}), 500

# User and friends endpoints
@api_bp.route('/user/profile', methods=['GET'])
@login_required
def get_profile():
    """API endpoint to get user profile."""
    return jsonify({
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'profile_image': current_user.profile_image
    })

@api_bp.route('/user/friends', methods=['GET'])
@login_required
def get_friends():
    """API endpoint to get user's friends."""
    connections = Connection.query.filter_by(
        user_id=current_user.id, 
        status='accepted'
    ).all()
    
    friends = []
    for conn in connections:
        friend = User.query.get(conn.friend_id)
        if friend:
            friends.append({
                'id': friend.id,
                'name': friend.name,
                'email': friend.email,
                'profile_image': friend.profile_image
            })
    
    return jsonify({'friends': friends})

# Purchase and sharing endpoints
@api_bp.route('/purchases', methods=['GET'])
@login_required
def get_purchases():
    """API endpoint to get user's purchases."""
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    
    result = []
    for purchase in purchases:
        product = Product.query.get(purchase.product_id)
        result.append({
            'id': purchase.id,
            'purchase_date': purchase.purchase_date.isoformat(),
            'is_shared': purchase.is_shared,
            'store_name': purchase.store_name,
            'product': {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'image_url': product.image_url,
                'price': float(product.price),
                'currency': product.currency,
                'category': product.category
            }
        })
    
    return jsonify({'purchases': result})

@api_bp.route('/purchases/<int:purchase_id>/share', methods=['PUT'])
@login_required
def share_purchase(purchase_id):
    """API endpoint to share a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    if purchase.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    purchase.is_shared = True
    purchase.share_comment = request.json.get('comment', '')
    db.session.commit()
    
    return jsonify({'message': 'Purchase shared successfully'})

@api_bp.route('/purchases/<int:purchase_id>/unshare', methods=['PUT'])
@login_required
def unshare_purchase(purchase_id):
    """API endpoint to unshare a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    if purchase.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    purchase.is_shared = False
    db.session.commit()
    
    return jsonify({'message': 'Purchase unshared successfully'})

@api_bp.route('/feed', methods=['GET'])
@login_required
def get_feed():
    """API endpoint to get social feed."""
    # Get friend IDs
    friend_connections = Connection.query.filter_by(
        user_id=current_user.id, 
        status='accepted'
    ).all()
    
    friend_ids = [conn.friend_id for conn in friend_connections]
    
    # Get shared purchases from friends
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    shared_purchases = Purchase.query.filter(
        Purchase.user_id.in_(friend_ids),
        Purchase.is_shared == True
    ).order_by(Purchase.purchase_date.desc()).paginate(page=page, per_page=per_page)
    
    result = []
    for purchase in shared_purchases.items:
        product = Product.query.get(purchase.product_id)
        user = User.query.get(purchase.user_id)
        
        # Get likes count
        likes_count = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='like'
        ).count()
        
        # Check if current user liked this
        user_liked = Interaction.query.filter_by(
            user_id=current_user.id,
            purchase_id=purchase.id,
            type='like'
        ).first() is not None
        
        # Check if current user saved this
        user_saved = Interaction.query.filter_by(
            user_id=current_user.id,
            purchase_id=purchase.id,
            type='save'
        ).first() is not None
        
        # Get comments
        comments = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='comment'
        ).order_by(Interaction.created_at.asc()).all()
        
        comments_data = []
        for comment in comments:
            comment_user = User.query.get(comment.user_id)
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'user': {
                    'id': comment_user.id,
                    'name': comment_user.name,
                    'profile_image': comment_user.profile_image
                }
            })
        
        result.append({
            'id': purchase.id,
            'purchase_date': purchase.purchase_date.isoformat(),
            'share_comment': purchase.share_comment,
            'user': {
                'id': user.id,
                'name': user.name,
                'profile_image': user.profile_image
            },
            'product': {
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'image_url': product.image_url,
                'price': float(product.price),
                'currency': product.currency,
                'category': product.category
            },
            'likes_count': likes_count,
            'user_liked': user_liked,
            'user_saved': user_saved,
            'comments': comments_data
        })
    
    return jsonify({
        'feed': result,
        'total': shared_purchases.total,
        'pages': shared_purchases.pages,
        'current_page': page
    })

# Analytics endpoints
@api_bp.route('/analytics/spending', methods=['GET'])
@login_required
def get_spending_analytics():
    """API endpoint to get monthly spending analytics."""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        analytics_data = AnalyticsService.get_monthly_spending(
            current_user.id, year=year, month=month
        )
        
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/categories', methods=['GET'])
@login_required
def get_category_analytics():
    """API endpoint to get category-based spending analytics."""
    try:
        from datetime import datetime, timedelta
        
        # Get date range from query parameters
        period_months = request.args.get('period_months', 12, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        analytics_data = AnalyticsService.get_category_spending_analysis(
            current_user.id, start_date=start_date, end_date=end_date
        )
        
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/stores', methods=['GET'])
@login_required
def get_store_analytics():
    """API endpoint to get store-based spending analytics."""
    try:
        from datetime import datetime, timedelta
        
        # Get date range from query parameters
        period_months = request.args.get('period_months', 12, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_months * 30)
        
        analytics_data = AnalyticsService.get_store_spending_analysis(
            current_user.id, start_date=start_date, end_date=end_date
        )
        
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/trends', methods=['GET'])
@login_required
def get_trend_analytics():
    """API endpoint to get spending trend analytics."""
    try:
        period_months = request.args.get('period_months', 12, type=int)
        
        analytics_data = AnalyticsService.get_spending_trends(
            current_user.id, period_months=period_months
        )
        
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/analytics/comprehensive', methods=['GET'])
@login_required
def get_comprehensive_analytics():
    """API endpoint to get comprehensive analytics combining all analysis types."""
    try:
        period_months = request.args.get('period_months', 12, type=int)
        
        analytics_data = AnalyticsService.get_comprehensive_analytics(
            current_user.id, period_months=period_months
        )
        
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Social interaction endpoints
@api_bp.route('/feed/item/<int:purchase_id>/like', methods=['POST'])
@login_required
def like_purchase_api(purchase_id):
    """API endpoint to like/unlike a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Check if already liked
    existing_like = Interaction.query.filter_by(
        user_id=current_user.id,
        purchase_id=purchase_id,
        type='like'
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        action = 'unliked'
        liked = False
        # Delete like notification
        NotificationService.delete_like_notification(purchase_id, current_user.id)
    else:
        # Like
        like = Interaction(
            user_id=current_user.id,
            purchase_id=purchase_id,
            type='like'
        )
        db.session.add(like)
        action = 'liked'
        liked = True
    
    db.session.commit()
    
    # Create like notification if liked
    if liked:
        NotificationService.create_like_notification(purchase_id, current_user.id)
    
    # Get updated likes count
    likes_count = Interaction.query.filter_by(
        purchase_id=purchase_id,
        type='like'
    ).count()
    
    return jsonify({
        'success': True,
        'action': action,
        'liked': liked,
        'likes_count': likes_count
    })

@api_bp.route('/feed/item/<int:purchase_id>/comment', methods=['POST'])
@login_required
def comment_purchase_api(purchase_id):
    """API endpoint to comment on a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Comment content is required'}), 400
    
    content = data['content'].strip()
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    comment = Interaction(
        user_id=current_user.id,
        purchase_id=purchase_id,
        type='comment',
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # Create comment notification
    NotificationService.create_comment_notification(purchase_id, current_user.id, content)
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': current_user.id,
                'name': current_user.name,
                'profile_image': current_user.profile_image
            }
        }
    })

@api_bp.route('/feed/item/<int:purchase_id>/save', methods=['POST'])
@login_required
def save_purchase_api(purchase_id):
    """API endpoint to save/unsave a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    
    # Check if already saved
    existing_save = Interaction.query.filter_by(
        user_id=current_user.id,
        purchase_id=purchase_id,
        type='save'
    ).first()
    
    if existing_save:
        # Unsave
        db.session.delete(existing_save)
        action = 'unsaved'
        saved = False
    else:
        # Save
        save = Interaction(
            user_id=current_user.id,
            purchase_id=purchase_id,
            type='save'
        )
        db.session.add(save)
        action = 'saved'
        saved = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action,
        'saved': saved
    })

@api_bp.route('/saved', methods=['GET'])
@login_required
def get_saved_purchases():
    """API endpoint to get user's saved purchases."""
    saved_interactions = Interaction.query.filter_by(
        user_id=current_user.id,
        type='save'
    ).order_by(Interaction.created_at.desc()).all()
    
    result = []
    for interaction in saved_interactions:
        purchase = Purchase.query.get(interaction.purchase_id)
        if purchase and purchase.is_shared:  # Only show shared purchases
            product = Product.query.get(purchase.product_id)
            user = User.query.get(purchase.user_id)
            
            result.append({
                'id': purchase.id,
                'purchase_date': purchase.purchase_date.isoformat(),
                'share_comment': purchase.share_comment,
                'saved_at': interaction.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'profile_image': user.profile_image
                },
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'image_url': product.image_url,
                    'price': float(product.price),
                    'currency': product.currency,
                    'category': product.category
                }
            })
    
    return jsonify({'saved_purchases': result})

# Notification endpoints
@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """API endpoint to get user notifications."""
    limit = request.args.get('limit', 20, type=int)
    unread_only = request.args.get('unread_only', False, type=bool)
    
    notifications = NotificationService.get_user_notifications(
        current_user.id, 
        limit=limit, 
        unread_only=unread_only
    )
    
    result = []
    for notification in notifications:
        notification_data = notification.to_dict()
        
        # Add related user info if available
        if notification.related_user_id:
            related_user = User.query.get(notification.related_user_id)
            if related_user:
                notification_data['related_user'] = {
                    'id': related_user.id,
                    'name': related_user.name,
                    'profile_image': related_user.profile_image
                }
        
        # Add related purchase info if available
        if notification.related_purchase_id:
            related_purchase = Purchase.query.get(notification.related_purchase_id)
            if related_purchase:
                product = Product.query.get(related_purchase.product_id)
                notification_data['related_purchase'] = {
                    'id': related_purchase.id,
                    'product_title': product.title if product else 'Unknown Product'
                }
        
        result.append(notification_data)
    
    return jsonify({
        'notifications': result,
        'unread_count': NotificationService.get_unread_count(current_user.id)
    })

@api_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """API endpoint to mark a notification as read."""
    success = NotificationService.mark_as_read(notification_id, current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': 'Notification marked as read'})
    else:
        return jsonify({'error': 'Notification not found'}), 404

@api_bp.route('/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_notifications_read():
    """API endpoint to mark all notifications as read."""
    count = NotificationService.mark_all_as_read(current_user.id)
    
    return jsonify({
        'success': True, 
        'message': f'{count} notifications marked as read'
    })

@api_bp.route('/notifications/unread-count', methods=['GET'])
@login_required
def get_unread_notifications_count():
    """API endpoint to get unread notifications count."""
    count = NotificationService.get_unread_count(current_user.id)
    return jsonify({'unread_count': count})