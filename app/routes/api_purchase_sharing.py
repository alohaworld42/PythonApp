from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_required, current_user
from datetime import datetime
import hmac
from app import db
from app.models.user import User
from app.models.purchase import Purchase
from app.models.product import Product
from app.models.connection import Connection
from app.models.interaction import Interaction
from app.services.notification_service import NotificationService

api_purchase_sharing_bp = Blueprint('api_purchase_sharing', __name__)

# CSRF Protection for API endpoints
def verify_csrf_token():
    """Verify CSRF token for state-changing operations."""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.get('_csrf_token')
        request_token = request.headers.get('X-CSRF-Token') or request.json.get('_csrf_token') if request.json else None
        
        if not token or not request_token or not hmac.compare_digest(token, request_token):
            return False
    return True

# Purchase endpoints
@api_purchase_sharing_bp.route('/purchases', methods=['GET'])
@login_required
def get_purchases():
    """API endpoint to get user's purchases."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        shared_only = request.args.get('shared_only', False, type=bool)
        category = request.args.get('category', '')
        store = request.args.get('store', '')
        sort_by = request.args.get('sort_by', 'purchase_date')  # purchase_date, price, title
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        # Validate pagination parameters
        if per_page > 100:
            per_page = 100
        if page < 1:
            page = 1
        
        # Build query
        query = Purchase.query.filter_by(user_id=current_user.id)
        
        if shared_only:
            query = query.filter(Purchase.is_shared == True)
        
        if store:
            query = query.filter(Purchase.store_name.ilike(f'%{store}%'))
        
        # Join with Product for category filtering and sorting
        query = query.join(Product)
        
        if category:
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        # Apply sorting
        if sort_by == 'purchase_date':
            if sort_order == 'asc':
                query = query.order_by(Purchase.purchase_date.asc())
            else:
                query = query.order_by(Purchase.purchase_date.desc())
        elif sort_by == 'price':
            if sort_order == 'asc':
                query = query.order_by(Product.price.asc())
            else:
                query = query.order_by(Product.price.desc())
        elif sort_by == 'title':
            if sort_order == 'asc':
                query = query.order_by(Product.title.asc())
            else:
                query = query.order_by(Product.title.desc())
        else:
            # Default sorting
            query = query.order_by(Purchase.purchase_date.desc())
        
        # Paginate results
        purchases_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        result = []
        for purchase in purchases_paginated.items:
            product = Product.query.get(purchase.product_id)
            
            # Get interaction counts
            likes_count = Interaction.query.filter_by(
                purchase_id=purchase.id,
                type='like'
            ).count()
            
            comments_count = Interaction.query.filter_by(
                purchase_id=purchase.id,
                type='comment'
            ).count()
            
            result.append({
                'id': purchase.id,
                'purchase_date': purchase.purchase_date.isoformat(),
                'is_shared': purchase.is_shared,
                'share_comment': purchase.share_comment,
                'store_name': purchase.store_name,
                'order_id': purchase.order_id,
                'created_at': purchase.created_at.isoformat(),
                'updated_at': purchase.updated_at.isoformat(),
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'image_url': product.image_url,
                    'price': float(product.price),
                    'currency': product.currency,
                    'category': product.category,
                    'source': product.source
                },
                'interactions': {
                    'likes_count': likes_count,
                    'comments_count': comments_count
                }
            })
        
        return jsonify({
            'purchases': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': purchases_paginated.total,
                'pages': purchases_paginated.pages,
                'has_next': purchases_paginated.has_next,
                'has_prev': purchases_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get purchases error: {str(e)}")
        return jsonify({'error': 'Failed to get purchases'}), 500

@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>', methods=['GET'])
@login_required
def get_purchase_detail(purchase_id):
    """API endpoint to get purchase details."""
    try:
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        # Check if user owns the purchase or if it's shared and they're friends
        if purchase.user_id != current_user.id:
            if not purchase.is_shared:
                return jsonify({'error': 'Purchase not accessible'}), 403
            
            # Check if users are friends
            connection = Connection.query.filter(
                ((Connection.user_id == current_user.id) & (Connection.friend_id == purchase.user_id)) |
                ((Connection.user_id == purchase.user_id) & (Connection.friend_id == current_user.id))
            ).filter(Connection.status == 'accepted').first()
            
            if not connection:
                return jsonify({'error': 'Purchase not accessible'}), 403
        
        product = Product.query.get(purchase.product_id)
        owner = User.query.get(purchase.user_id)
        
        # Get interactions
        likes = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='like'
        ).all()
        
        comments = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='comment'
        ).order_by(Interaction.created_at.asc()).all()
        
        # Check if current user liked or saved this purchase
        user_liked = any(like.user_id == current_user.id for like in likes)
        user_saved = Interaction.query.filter_by(
            user_id=current_user.id,
            purchase_id=purchase.id,
            type='save'
        ).first() is not None
        
        # Format likes
        likes_data = []
        for like in likes:
            like_user = User.query.get(like.user_id)
            likes_data.append({
                'id': like.id,
                'user': {
                    'id': like_user.id,
                    'name': like_user.name,
                    'profile_image': like_user.profile_image
                },
                'created_at': like.created_at.isoformat()
            })
        
        # Format comments
        comments_data = []
        for comment in comments:
            comment_user = User.query.get(comment.user_id)
            comments_data.append({
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'id': comment_user.id,
                    'name': comment_user.name,
                    'profile_image': comment_user.profile_image
                },
                'created_at': comment.created_at.isoformat()
            })
        
        return jsonify({
            'purchase': {
                'id': purchase.id,
                'purchase_date': purchase.purchase_date.isoformat(),
                'is_shared': purchase.is_shared,
                'share_comment': purchase.share_comment,
                'store_name': purchase.store_name,
                'order_id': purchase.order_id,
                'created_at': purchase.created_at.isoformat(),
                'updated_at': purchase.updated_at.isoformat(),
                'owner': {
                    'id': owner.id,
                    'name': owner.name,
                    'profile_image': owner.profile_image
                },
                'product': {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'image_url': product.image_url,
                    'price': float(product.price),
                    'currency': product.currency,
                    'category': product.category,
                    'source': product.source
                },
                'interactions': {
                    'likes': likes_data,
                    'comments': comments_data,
                    'likes_count': len(likes_data),
                    'comments_count': len(comments_data),
                    'user_liked': user_liked,
                    'user_saved': user_saved
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get purchase detail error: {str(e)}")
        return jsonify({'error': 'Failed to get purchase details'}), 500

# Sharing endpoints
@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>/share', methods=['PUT'])
@login_required
def share_purchase(purchase_id):
    """API endpoint to share a purchase."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        if purchase.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to share this purchase'}), 403
        
        data = request.get_json() or {}
        comment = data.get('comment', '').strip()
        
        purchase.is_shared = True
        purchase.share_comment = comment
        purchase.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase shared successfully',
            'purchase': {
                'id': purchase.id,
                'is_shared': purchase.is_shared,
                'share_comment': purchase.share_comment,
                'updated_at': purchase.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Share purchase error: {str(e)}")
        return jsonify({'error': 'Failed to share purchase'}), 500

@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>/unshare', methods=['PUT'])
@login_required
def unshare_purchase(purchase_id):
    """API endpoint to unshare a purchase."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        if purchase.user_id != current_user.id:
            return jsonify({'error': 'Not authorized to unshare this purchase'}), 403
        
        purchase.is_shared = False
        purchase.share_comment = None
        purchase.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase unshared successfully',
            'purchase': {
                'id': purchase.id,
                'is_shared': purchase.is_shared,
                'share_comment': purchase.share_comment,
                'updated_at': purchase.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Unshare purchase error: {str(e)}")
        return jsonify({'error': 'Failed to unshare purchase'}), 500

# Feed endpoints
@api_purchase_sharing_bp.route('/feed', methods=['GET'])
@login_required
def get_feed():
    """API endpoint to get social feed of friends' shared purchases."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        friend_id = request.args.get('friend_id', type=int)  # Filter by specific friend
        category = request.args.get('category', '')
        
        # Validate pagination parameters
        if per_page > 50:
            per_page = 50
        if page < 1:
            page = 1
        
        # Get friend IDs
        friend_connections = Connection.query.filter(
            ((Connection.user_id == current_user.id) | (Connection.friend_id == current_user.id)) &
            (Connection.status == 'accepted')
        ).all()
        
        friend_ids = set()
        for conn in friend_connections:
            if conn.user_id == current_user.id:
                friend_ids.add(conn.friend_id)
            else:
                friend_ids.add(conn.user_id)
        
        if not friend_ids:
            return jsonify({
                'feed': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0,
                    'has_next': False,
                    'has_prev': False
                }
            }), 200
        
        # Build query for shared purchases from friends
        query = Purchase.query.filter(
            Purchase.user_id.in_(friend_ids) &
            (Purchase.is_shared == True)
        )
        
        # Filter by specific friend if requested
        if friend_id:
            if friend_id not in friend_ids:
                return jsonify({'error': 'Not friends with specified user'}), 403
            query = query.filter(Purchase.user_id == friend_id)
        
        # Join with Product for category filtering
        query = query.join(Product)
        
        if category:
            query = query.filter(Product.category.ilike(f'%{category}%'))
        
        # Order by purchase date (newest first)
        query = query.order_by(Purchase.purchase_date.desc())
        
        # Paginate results
        feed_paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = []
        for purchase in feed_paginated.items:
            product = Product.query.get(purchase.product_id)
            user = User.query.get(purchase.user_id)
            
            # Get interaction counts
            likes_count = Interaction.query.filter_by(
                purchase_id=purchase.id,
                type='like'
            ).count()
            
            comments_count = Interaction.query.filter_by(
                purchase_id=purchase.id,
                type='comment'
            ).count()
            
            # Check if current user liked or saved this
            user_liked = Interaction.query.filter_by(
                user_id=current_user.id,
                purchase_id=purchase.id,
                type='like'
            ).first() is not None
            
            user_saved = Interaction.query.filter_by(
                user_id=current_user.id,
                purchase_id=purchase.id,
                type='save'
            ).first() is not None
            
            # Get recent comments (last 3)
            recent_comments = Interaction.query.filter_by(
                purchase_id=purchase.id,
                type='comment'
            ).order_by(Interaction.created_at.desc()).limit(3).all()
            
            comments_data = []
            for comment in reversed(recent_comments):  # Show oldest first
                comment_user = User.query.get(comment.user_id)
                comments_data.append({
                    'id': comment.id,
                    'content': comment.content,
                    'user': {
                        'id': comment_user.id,
                        'name': comment_user.name,
                        'profile_image': comment_user.profile_image
                    },
                    'created_at': comment.created_at.isoformat()
                })
            
            result.append({
                'id': purchase.id,
                'purchase_date': purchase.purchase_date.isoformat(),
                'share_comment': purchase.share_comment,
                'store_name': purchase.store_name,
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
                    'category': product.category,
                    'source': product.source
                },
                'interactions': {
                    'likes_count': likes_count,
                    'comments_count': comments_count,
                    'user_liked': user_liked,
                    'user_saved': user_saved,
                    'recent_comments': comments_data
                }
            })
        
        return jsonify({
            'feed': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': feed_paginated.total,
                'pages': feed_paginated.pages,
                'has_next': feed_paginated.has_next,
                'has_prev': feed_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get feed error: {str(e)}")
        return jsonify({'error': 'Failed to get feed'}), 500

# Interaction endpoints
@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>/like', methods=['POST'])
@login_required
def like_purchase(purchase_id):
    """API endpoint to like/unlike a purchase."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        # Check if purchase is accessible (shared and user is friend, or user owns it)
        if purchase.user_id != current_user.id:
            if not purchase.is_shared:
                return jsonify({'error': 'Purchase not accessible'}), 403
            
            # Check if users are friends
            connection = Connection.query.filter(
                ((Connection.user_id == current_user.id) & (Connection.friend_id == purchase.user_id)) |
                ((Connection.user_id == purchase.user_id) & (Connection.friend_id == current_user.id))
            ).filter(Connection.status == 'accepted').first()
            
            if not connection:
                return jsonify({'error': 'Purchase not accessible'}), 403
        
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
            
            # Delete like notification if it exists
            try:
                NotificationService.delete_like_notification(purchase_id, current_user.id)
            except:
                pass  # Notification service might not be fully implemented
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
            
            # Create like notification if not liking own purchase
            if purchase.user_id != current_user.id:
                try:
                    NotificationService.create_like_notification(purchase_id, current_user.id)
                except:
                    pass  # Notification service might not be fully implemented
        
        db.session.commit()
        
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
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Like purchase error: {str(e)}")
        return jsonify({'error': 'Failed to like/unlike purchase'}), 500

@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>/comment', methods=['POST'])
@login_required
def comment_purchase(purchase_id):
    """API endpoint to comment on a purchase."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        # Check if purchase is accessible
        if purchase.user_id != current_user.id:
            if not purchase.is_shared:
                return jsonify({'error': 'Purchase not accessible'}), 403
            
            # Check if users are friends
            connection = Connection.query.filter(
                ((Connection.user_id == current_user.id) & (Connection.friend_id == purchase.user_id)) |
                ((Connection.user_id == purchase.user_id) & (Connection.friend_id == current_user.id))
            ).filter(Connection.status == 'accepted').first()
            
            if not connection:
                return jsonify({'error': 'Purchase not accessible'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Comment content is required'}), 400
        
        content = data['content'].strip()
        if not content:
            return jsonify({'error': 'Comment cannot be empty'}), 400
        
        if len(content) > 1000:
            return jsonify({'error': 'Comment is too long (max 1000 characters)'}), 400
        
        comment = Interaction(
            user_id=current_user.id,
            purchase_id=purchase_id,
            type='comment',
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # Create comment notification if not commenting on own purchase
        if purchase.user_id != current_user.id:
            try:
                NotificationService.create_comment_notification(purchase_id, current_user.id, content)
            except:
                pass  # Notification service might not be fully implemented
        
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
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Comment purchase error: {str(e)}")
        return jsonify({'error': 'Failed to add comment'}), 500

@api_purchase_sharing_bp.route('/purchases/<int:purchase_id>/save', methods=['POST'])
@login_required
def save_purchase(purchase_id):
    """API endpoint to save/unsave a purchase."""
    try:
        # Verify CSRF token
        if not verify_csrf_token():
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        purchase = Purchase.query.get(purchase_id)
        
        if not purchase:
            return jsonify({'error': 'Purchase not found'}), 404
        
        # Check if purchase is accessible
        if purchase.user_id != current_user.id:
            if not purchase.is_shared:
                return jsonify({'error': 'Purchase not accessible'}), 403
            
            # Check if users are friends
            connection = Connection.query.filter(
                ((Connection.user_id == current_user.id) & (Connection.friend_id == purchase.user_id)) |
                ((Connection.user_id == purchase.user_id) & (Connection.friend_id == current_user.id))
            ).filter(Connection.status == 'accepted').first()
            
            if not connection:
                return jsonify({'error': 'Purchase not accessible'}), 403
        
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
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Save purchase error: {str(e)}")
        return jsonify({'error': 'Failed to save/unsave purchase'}), 500

@api_purchase_sharing_bp.route('/saved', methods=['GET'])
@login_required
def get_saved_purchases():
    """API endpoint to get user's saved purchases."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination parameters
        if per_page > 50:
            per_page = 50
        if page < 1:
            page = 1
        
        # Get saved interactions
        saved_query = Interaction.query.filter_by(
            user_id=current_user.id,
            type='save'
        ).order_by(Interaction.created_at.desc())
        
        saved_paginated = saved_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        result = []
        for interaction in saved_paginated.items:
            purchase = Purchase.query.get(interaction.purchase_id)
            
            # Only show if purchase still exists and is shared (or user owns it)
            if purchase and (purchase.is_shared or purchase.user_id == current_user.id):
                product = Product.query.get(purchase.product_id)
                user = User.query.get(purchase.user_id)
                
                result.append({
                    'id': purchase.id,
                    'purchase_date': purchase.purchase_date.isoformat(),
                    'share_comment': purchase.share_comment,
                    'store_name': purchase.store_name,
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
                        'category': product.category,
                        'source': product.source
                    }
                })
        
        return jsonify({
            'saved_purchases': result,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': saved_paginated.total,
                'pages': saved_paginated.pages,
                'has_next': saved_paginated.has_next,
                'has_prev': saved_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get saved purchases error: {str(e)}")
        return jsonify({'error': 'Failed to get saved purchases'}), 500

# Categories and stats endpoints
@api_purchase_sharing_bp.route('/purchases/categories', methods=['GET'])
@login_required
def get_purchase_categories():
    """API endpoint to get user's purchase categories."""
    try:
        # Get distinct categories from user's purchases
        categories = db.session.query(Product.category).join(Purchase).filter(
            Purchase.user_id == current_user.id,
            Product.category.isnot(None),
            Product.category != ''
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        category_list.sort()
        
        return jsonify({
            'categories': category_list,
            'count': len(category_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get purchase categories error: {str(e)}")
        return jsonify({'error': 'Failed to get categories'}), 500

@api_purchase_sharing_bp.route('/purchases/stores', methods=['GET'])
@login_required
def get_purchase_stores():
    """API endpoint to get user's purchase stores."""
    try:
        # Get distinct stores from user's purchases
        stores = db.session.query(Purchase.store_name).filter(
            Purchase.user_id == current_user.id,
            Purchase.store_name.isnot(None),
            Purchase.store_name != ''
        ).distinct().all()
        
        store_list = [store[0] for store in stores if store[0]]
        store_list.sort()
        
        return jsonify({
            'stores': store_list,
            'count': len(store_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get purchase stores error: {str(e)}")
        return jsonify({'error': 'Failed to get stores'}), 500