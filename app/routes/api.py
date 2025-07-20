from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.models.store_integration import StoreIntegration
from app.integrations.shopify import ShopifyClient
from app.integrations.woocommerce import WooCommerceClient

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
    """API endpoint to get spending analytics."""
    # This would be implemented with actual analytics calculations
    return jsonify({
        'total_spending': 1250.00,
        'average_order': 62.50,
        'order_count': 20
    })

@api_bp.route('/analytics/categories', methods=['GET'])
@login_required
def get_category_analytics():
    """API endpoint to get category-based analytics."""
    # This would be implemented with actual analytics calculations
    return jsonify({
        'categories': [
            {'name': 'Electronics', 'amount': 450.00, 'count': 3},
            {'name': 'Clothing', 'amount': 320.00, 'count': 8},
            {'name': 'Home', 'amount': 280.00, 'count': 5},
            {'name': 'Other', 'amount': 200.00, 'count': 4}
        ]
    })

@api_bp.route('/analytics/stores', methods=['GET'])
@login_required
def get_store_analytics():
    """API endpoint to get store-based analytics."""
    # This would be implemented with actual analytics calculations
    return jsonify({
        'stores': [
            {'name': 'Amazon', 'amount': 520.00, 'count': 7},
            {'name': 'Shopify Store 1', 'amount': 350.00, 'count': 5},
            {'name': 'WooCommerce Store', 'amount': 280.00, 'count': 6},
            {'name': 'Other', 'amount': 100.00, 'count': 2}
        ]
    })

@api_bp.route('/analytics/trends', methods=['GET'])
@login_required
def get_trend_analytics():
    """API endpoint to get spending trend analytics."""
    # This would be implemented with actual analytics calculations
    return jsonify({
        'trends': [
            {'month': 'Jan', 'amount': 120.00},
            {'month': 'Feb', 'amount': 180.00},
            {'month': 'Mar', 'amount': 250.00},
            {'month': 'Apr', 'amount': 200.00},
            {'month': 'May', 'amount': 300.00},
            {'month': 'Jun', 'amount': 200.00}
        ]
    })