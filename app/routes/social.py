from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.connection import Connection
from app.models.purchase import Purchase
from app.models.interaction import Interaction

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
    """Social feed route."""
    # Get friend IDs
    friend_connections = Connection.query.filter_by(
        user_id=current_user.id, 
        status='accepted'
    ).all()
    
    friend_ids = [conn.friend_id for conn in friend_connections]
    
    # Get shared purchases from friends
    shared_purchases = Purchase.query.filter(
        Purchase.user_id.in_(friend_ids),
        Purchase.is_shared == True
    ).order_by(Purchase.purchase_date.desc()).all()
    
    return render_template(
        'social/feed.html', 
        title='Friend Feed', 
        shared_purchases=shared_purchases
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
    
    flash('Comment added!', 'success')
    return redirect(url_for('social.feed'))