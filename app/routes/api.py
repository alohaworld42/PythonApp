from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
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

# Authentication endpoints
@api_bp.route('/auth/register', methods=['POST'])
def register():
    """API endpoint for user registration."""
    data = request.get_json()
    
    # Validate data
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user = User(
        email=data['email'],
        name=data.get('name', ''),
        password_hash=User.hash_password(data['password'])
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201

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