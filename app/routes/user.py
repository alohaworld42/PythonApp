import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from app import db, bcrypt
from app.models.user import User
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.utils.forms import (
    UpdateProfileForm, ChangePasswordForm, 
    PrivacySettingsForm, NotificationSettingsForm
)

user_bp = Blueprint('user', __name__)

def save_profile_picture(form_picture):
    """Save profile picture with a random name."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', 'images', 'profiles', picture_fn)
    
    # Resize image
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route."""
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file = save_profile_picture(form.profile_image.data)
            current_user.profile_image = picture_file
        
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    
    return render_template('user/profile.html', title='Profile', form=form)

@user_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.password_hash = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('user/change_password.html', title='Change Password', form=form)

@user_bp.route('/privacy_settings', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    """Privacy settings route."""
    form = PrivacySettingsForm()
    
    # Get user settings from database
    settings = current_user.settings or {}
    
    if form.validate_on_submit():
        # Update settings
        settings['privacy'] = {
            'profile_visibility': form.profile_visibility.data,
            'show_email': form.show_email.data,
            'default_sharing': form.default_sharing.data,
            'show_price': form.show_price.data,
            'friend_requests': form.friend_requests.data,
            'analytics_consent': form.analytics_consent.data,
            'personalized_recommendations': form.personalized_recommendations.data
        }
        
        current_user.settings = settings
        db.session.commit()
        flash('Your privacy settings have been updated!', 'success')
        return redirect(url_for('user.privacy_settings'))
    elif request.method == 'GET':
        # Set form defaults from user settings
        privacy = settings.get('privacy', {})
        form.profile_visibility.data = privacy.get('profile_visibility', True)
        form.show_email.data = privacy.get('show_email', False)
        form.default_sharing.data = privacy.get('default_sharing', False)
        form.show_price.data = privacy.get('show_price', True)
        form.friend_requests.data = privacy.get('friend_requests', 'everyone')
        form.analytics_consent.data = privacy.get('analytics_consent', True)
        form.personalized_recommendations.data = privacy.get('personalized_recommendations', True)
    
    return render_template('user/privacy_settings.html', title='Privacy Settings', form=form)

@user_bp.route('/notification_settings', methods=['GET', 'POST'])
@login_required
def notification_settings():
    """Notification settings route."""
    form = NotificationSettingsForm()
    
    # Get user settings from database
    settings = current_user.settings or {}
    
    if form.validate_on_submit():
        # Update settings
        settings['notifications'] = {
            'email': {
                'friend_requests': form.email_friend_requests.data,
                'comments': form.email_comments.data,
                'likes': form.email_likes.data,
                'new_friend_purchases': form.email_new_friend_purchases.data,
                'system_updates': form.email_system_updates.data
            },
            'app': {
                'friend_requests': form.app_friend_requests.data,
                'comments': form.app_comments.data,
                'likes': form.app_likes.data,
                'new_friend_purchases': form.app_new_friend_purchases.data,
                'system_updates': form.app_system_updates.data
            },
            'frequency': form.notification_frequency.data
        }
        
        current_user.settings = settings
        db.session.commit()
        flash('Your notification settings have been updated!', 'success')
        return redirect(url_for('user.notification_settings'))
    elif request.method == 'GET':
        # Set form defaults from user settings
        notifications = settings.get('notifications', {})
        email = notifications.get('email', {})
        app = notifications.get('app', {})
        
        form.email_friend_requests.data = email.get('friend_requests', True)
        form.email_comments.data = email.get('comments', True)
        form.email_likes.data = email.get('likes', False)
        form.email_new_friend_purchases.data = email.get('new_friend_purchases', False)
        form.email_system_updates.data = email.get('system_updates', True)
        
        form.app_friend_requests.data = app.get('friend_requests', True)
        form.app_comments.data = app.get('comments', True)
        form.app_likes.data = app.get('likes', True)
        form.app_new_friend_purchases.data = app.get('new_friend_purchases', True)
        form.app_system_updates.data = app.get('system_updates', True)
        
        form.notification_frequency.data = notifications.get('frequency', 'immediate')
    
    return render_template('user/notification_settings.html', title='Notification Settings', form=form)

@user_bp.route('/purchases')
@login_required
def purchases():
    """User purchases route."""
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    return render_template('user/purchases.html', title='My Purchases', purchases=purchases)

@user_bp.route('/purchases/<int:purchase_id>/toggle_share', methods=['POST'])
@login_required
def toggle_share(purchase_id):
    """Toggle sharing status of a purchase."""
    purchase = Purchase.query.get_or_404(purchase_id)
    if purchase.user_id != current_user.id:
        flash('You do not have permission to modify this purchase.', 'danger')
        return redirect(url_for('user.purchases'))
    
    purchase.is_shared = not purchase.is_shared
    db.session.commit()
    
    flash('Sharing status updated!', 'success')
    return redirect(url_for('user.purchases'))

@user_bp.route('/analytics')
@login_required
def analytics():
    """User analytics route."""
    # Get analytics data
    return render_template('user/analytics.html', title='My Analytics')

@user_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account."""
    # Delete user data
    # This would include cascading deletes for purchases, connections, etc.
    
    # For now, just log the user out
    logout_user()
    flash('Your account has been deleted.', 'info')
    return redirect(url_for('main.index'))