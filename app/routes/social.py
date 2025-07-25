from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.connection import Connection
from app.models.purchase import Purchase
from app.models.interaction import Interaction
from app.services.notification_service import NotificationService

social_bp = Blueprint('social', __name__)

@social_bp.route('/friends')
@login_required
def friends():
    """Friends list route."""
    # Get accepted connections
    friends = Connection.query.filter_by(
        user_id=current_user.id, 
        status='accepted'
    ).all()
    
    # Get pending friend requests
    pending_requests = Connection.query.filter_by(
        friend_id=current_user.id, 
        status='pending'
    ).all()
    
    return render_template(
        'social/friends.html', 
        title='Friends', 
        friends=friends, 
        pending_requests=pending_requests
    )

@social_bp.route('/friends/search', methods=['GET', 'POST'])
@login_required
def search_friends():
    """Friend search route."""
    if request.method == 'POST':
        search_term = request.form.get('search_term', '')
        users = User.query.filter(User.email.like(f'%{search_term}%') | 
                                 User.name.like(f'%{search_term}%')).all()
        
        # Filter out current user and existing connections
        existing_connections = Connection.query.filter_by(user_id=current_user.id).all()
        existing_connection_ids = [conn.friend_id for conn in existing_connections]
        
        users = [user for user in users if user.id != current_user.id and 
                user.id not in existing_connection_ids]
        
        return render_template(
            'social/search_results.html', 
            title='Search Results', 
            users=users
        )
    
    return render_template('social/search.html', title='Find Friends')

@social_bp.route('/friends/request/<int:user_id>', methods=['POST'])
@login_required
def send_friend_request(user_id):
    """Send friend request route."""
    if user_id == current_user.id:
        flash('You cannot send a friend request to yourself.', 'danger')
        return redirect(url_for('social.search_friends'))
    
    # Check if connection already exists
    existing_connection = Connection.query.filter_by(
        user_id=current_user.id, 
        friend_id=user_id
    ).first()
    
    if existing_connection:
        flash('A connection with this user already exists.', 'warning')
        return redirect(url_for('social.friends'))
    
    # Create new connection
    connection = Connection(
        user_id=current_user.id,
        friend_id=user_id,
        status='pending'
    )
    
    db.session.add(connection)
    db.session.commit()
    
    # Create friend request notification
    NotificationService.create_friend_request_notification(user_id, current_user.id)
    
    flash('Friend request sent!', 'success')
    return redirect(url_for('social.friends'))

@social_bp.route('/friends/accept/<int:connection_id>', methods=['POST'])
@login_required
def accept_friend_request(connection_id):
    """Accept friend request route."""
    connection = Connection.query.get_or_404(connection_id)
    
    if connection.friend_id != current_user.id:
        flash('You do not have permission to accept this request.', 'danger')
        return redirect(url_for('social.friends'))
    
    # Accept the request
    connection.status = 'accepted'
    
    # Create reverse connection
    reverse_connection = Connection(
        user_id=connection.friend_id,
        friend_id=connection.user_id,
        status='accepted'
    )
    
    db.session.add(reverse_connection)
    db.session.commit()
    
    flash('Friend request accepted!', 'success')
    return redirect(url_for('social.friends'))

@social_bp.route('/friends/reject/<int:connection_id>', methods=['POST'])
@login_required
def reject_friend_request(connection_id):
    """Reject friend request route."""
    connection = Connection.query.get_or_404(connection_id)
    
    if connection.friend_id != current_user.id:
        flash('You do not have permission to reject this request.', 'danger')
        return redirect(url_for('social.friends'))
    
    # Delete the connection
    db.session.delete(connection)
    db.session.commit()
    
    flash('Friend request rejected.', 'info')
    return redirect(url_for('social.friends'))

@social_bp.route('/friends/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_friend(user_id):
    """Remove friend route."""
    # Delete both connections
    Connection.query.filter_by(user_id=current_user.id, friend_id=user_id).delete()
    Connection.query.filter_by(user_id=user_id, friend_id=current_user.id).delete()
    
    db.session.commit()
    
    flash('Friend removed.', 'info')
    return redirect(url_for('social.friends'))

@social_bp.route('/feed')
@login_required
def feed():
    """Social feed route with pagination support."""
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    # Get friend IDs
    friend_connections = Connection.query.filter_by(
        user_id=current_user.id, 
        status='accepted'
    ).all()
    
    friend_ids = [conn.friend_id for conn in friend_connections]
    
    if not friend_ids:
        # No friends, return empty feed
        return render_template(
            'social/feed.html', 
            title='Friend Feed', 
            shared_purchases=[],
            has_more=False,
            next_page=None
        )
    
    # Get shared purchases from friends with pagination
    # Order by updated_at to show recently shared/updated items first, then by purchase_date
    shared_purchases_query = Purchase.query.filter(
        Purchase.user_id.in_(friend_ids),
        Purchase.is_shared == True
    ).order_by(Purchase.updated_at.desc(), Purchase.purchase_date.desc())
    
    # Paginate results
    pagination = shared_purchases_query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    shared_purchases = pagination.items
    has_more = pagination.has_next
    next_page = pagination.next_num if has_more else None
    
    # For AJAX requests, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from flask import jsonify
        
        # Render individual feed items
        feed_items_html = []
        for purchase in shared_purchases:
            # Get interaction counts
            likes_count = Interaction.query.filter_by(
                purchase_id=purchase.id, 
                type='like'
            ).count()
            
            comments_count = Interaction.query.filter_by(
                purchase_id=purchase.id, 
                type='comment'
            ).count()
            
            # Check if current user has liked or saved this item
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
            
            # Render the feed item template
            item_html = render_template(
                'social/feed_item.html',
                purchase=purchase,
                likes_count=likes_count,
                comments_count=comments_count,
                user_liked=user_liked,
                user_saved=user_saved
            )
            feed_items_html.append(item_html)
        
        return jsonify({
            'items': feed_items_html,
            'has_more': has_more,
            'next_page': next_page
        })
    
    # For regular requests, get interaction data for initial load
    feed_data = []
    for purchase in shared_purchases:
        likes_count = Interaction.query.filter_by(
            purchase_id=purchase.id, 
            type='like'
        ).count()
        
        comments_count = Interaction.query.filter_by(
            purchase_id=purchase.id, 
            type='comment'
        ).count()
        
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
        
        feed_data.append({
            'purchase': purchase,
            'likes_count': likes_count,
            'comments_count': comments_count,
            'user_liked': user_liked,
            'user_saved': user_saved
        })
    
    return render_template(
        'social/feed.html', 
        title='Friend Feed', 
        feed_data=feed_data,
        has_more=has_more,
        next_page=next_page
    )

@social_bp.route('/feed/like/<int:purchase_id>', methods=['POST'])
@login_required
def like_purchase(purchase_id):
    """Like a purchase in the feed."""
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
    
    db.session.commit()
    
    # Create like notification if liked
    if action == 'liked':
        NotificationService.create_like_notification(purchase_id, current_user.id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'action': action})
    
    return redirect(url_for('social.feed'))

@social_bp.route('/feed/comment/<int:purchase_id>', methods=['POST'])
@login_required
def comment_purchase(purchase_id):
    """Comment on a purchase in the feed."""
    purchase = Purchase.query.get_or_404(purchase_id)
    content = request.form.get('content', '')
    
    if not content:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('social.feed'))
    
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
    
    flash('Comment added!', 'success')
    return redirect(url_for('social.feed'))

@social_bp.route('/feed/save/<int:purchase_id>', methods=['POST'])
@login_required
def save_purchase(purchase_id):
    """Save/unsave a purchase in the feed."""
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
        flash('Item removed from saved items.', 'info')
    else:
        # Save
        save = Interaction(
            user_id=current_user.id,
            purchase_id=purchase_id,
            type='save'
        )
        db.session.add(save)
        action = 'saved'
        flash('Item saved!', 'success')
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'action': action})
    
    return redirect(url_for('social.feed'))

@social_bp.route('/saved')
@login_required
def saved_items():
    """View saved items route."""
    saved_interactions = Interaction.query.filter_by(
        user_id=current_user.id,
        type='save'
    ).order_by(Interaction.created_at.desc()).all()
    
    saved_purchases = []
    for interaction in saved_interactions:
        purchase = Purchase.query.get(interaction.purchase_id)
        if purchase and purchase.is_shared:  # Only show shared purchases
            saved_purchases.append({
                'purchase': purchase,
                'saved_at': interaction.created_at
            })
    
    return render_template(
        'social/saved.html', 
        title='Saved Items', 
        saved_purchases=saved_purchases
    )

@social_bp.route('/notifications')
@login_required
def notifications():
    """View notifications route."""
    notifications = NotificationService.get_user_notifications(current_user.id, limit=50)
    unread_count = NotificationService.get_unread_count(current_user.id)
    
    return render_template(
        'social/notifications.html', 
        title='Notifications', 
        notifications=notifications,
        unread_count=unread_count
    )

@social_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read_route(notification_id):
    """Mark notification as read route."""
    success = NotificationService.mark_as_read(notification_id, current_user.id)
    
    if success:
        flash('Notification marked as read.', 'success')
    else:
        flash('Notification not found.', 'error')
    
    return redirect(url_for('social.notifications'))

@social_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read_route():
    """Mark all notifications as read route."""
    count = NotificationService.mark_all_as_read(current_user.id)
    
    flash(f'{count} notifications marked as read.', 'success')
    return redirect(url_for('social.notifications'))