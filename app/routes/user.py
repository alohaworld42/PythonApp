import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user, logout_user
from app import db, bcrypt
from app.models.user import User
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.services.purchase_sharing_service import PurchaseSharingService
from app.utils.forms import (
    UpdateProfileForm, ChangePasswordForm, 
    PrivacySettingsForm, NotificationSettingsForm,
    DashboardSettingsForm
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
    share_comment = request.form.get('share_comment', '')
    
    result = PurchaseSharingService.toggle_sharing(
        purchase_id, 
        current_user.id, 
        share_comment if share_comment else None
    )
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result)
    
    return redirect(request.referrer or url_for('user.purchases'))

@user_bp.route('/purchases/<int:purchase_id>/update_comment', methods=['POST'])
@login_required
def update_share_comment(purchase_id):
    """Update share comment for a purchase."""
    comment = request.form.get('comment', '').strip()
    
    result = PurchaseSharingService.update_share_comment(
        purchase_id, 
        current_user.id, 
        comment
    )
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash(result['message'], 'danger')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(result)
    
    return redirect(request.referrer or url_for('user.purchases'))

@user_bp.route('/purchases/bulk_share', methods=['POST'])
@login_required
def bulk_share():
    """Bulk update sharing status for multiple purchases."""
    purchase_ids = request.form.getlist('purchase_ids')
    action = request.form.get('action')  # 'share' or 'unshare'
    
    if not purchase_ids or action not in ['share', 'unshare']:
        flash('Invalid request.', 'danger')
        return redirect(url_for('user.purchases'))
    
    # Convert to integers
    try:
        purchase_ids = [int(pid) for pid in purchase_ids]
    except ValueError:
        flash('Invalid purchase IDs.', 'danger')
        return redirect(url_for('user.purchases'))
    
    is_shared = action == 'share'
    result = PurchaseSharingService.bulk_update_sharing(
        current_user.id, 
        purchase_ids, 
        is_shared
    )
    
    if result['success']:
        flash(result['message'], 'success')
    else:
        flash('Failed to update purchases.', 'danger')
    
    return redirect(url_for('user.purchases'))

@user_bp.route('/purchases/shared')
@login_required
def shared_purchases():
    """View user's shared purchases."""
    shared_purchases = PurchaseSharingService.get_user_shared_purchases(current_user.id)
    stats = PurchaseSharingService.get_sharing_stats(current_user.id)
    
    return render_template(
        'user/shared_purchases.html', 
        title='Shared Purchases', 
        purchases=shared_purchases,
        stats=stats
    )

@user_bp.route('/dashboard_settings', methods=['GET', 'POST'])
@login_required
def dashboard_settings():
    """Dashboard customization settings route."""
    form = DashboardSettingsForm()
    
    # Get user settings from database
    settings = current_user.settings or {}
    
    if form.validate_on_submit():
        # Update dashboard settings
        settings['dashboard'] = {
            'default_view': form.default_view.data,
            'items_per_page': int(form.items_per_page.data),
            'default_sort': form.default_sort.data,
            'widgets': {
                'show_quick_stats': form.show_quick_stats.data,
                'show_friend_activity': form.show_friend_activity.data,
                'show_recent_purchases': form.show_recent_purchases.data,
                'show_spending_chart': form.show_spending_chart.data,
                'order': form.widget_order.data
            },
            'layout': {
                'sidebar_collapsed': form.sidebar_collapsed.data,
                'compact_mode': form.compact_mode.data
            }
        }
        
        current_user.settings = settings
        db.session.commit()
        flash('Your dashboard settings have been updated!', 'success')
        return redirect(url_for('user.dashboard_settings'))
    elif request.method == 'GET':
        # Set form defaults from user settings
        dashboard = settings.get('dashboard', {})
        widgets = dashboard.get('widgets', {})
        layout = dashboard.get('layout', {})
        
        form.default_view.data = dashboard.get('default_view', 'grid')
        form.items_per_page.data = str(dashboard.get('items_per_page', 12))
        form.default_sort.data = dashboard.get('default_sort', 'date-desc')
        
        form.show_quick_stats.data = widgets.get('show_quick_stats', True)
        form.show_friend_activity.data = widgets.get('show_friend_activity', True)
        form.show_recent_purchases.data = widgets.get('show_recent_purchases', True)
        form.show_spending_chart.data = widgets.get('show_spending_chart', False)
        form.widget_order.data = widgets.get('order', '["quick_stats", "recent_purchases", "friend_activity"]')
        
        form.sidebar_collapsed.data = layout.get('sidebar_collapsed', False)
        form.compact_mode.data = layout.get('compact_mode', False)
    
    return render_template('user/dashboard_settings.html', title='Dashboard Settings', form=form)

@user_bp.route('/dashboard_settings/reset', methods=['POST'])
@login_required
def reset_dashboard_settings():
    """Reset dashboard settings to defaults."""
    settings = current_user.settings or {}
    
    # Reset dashboard settings to defaults
    settings['dashboard'] = {
        'default_view': 'grid',
        'items_per_page': 12,
        'default_sort': 'date-desc',
        'widgets': {
            'show_quick_stats': True,
            'show_friend_activity': True,
            'show_recent_purchases': True,
            'show_spending_chart': False,
            'order': '["quick_stats", "recent_purchases", "friend_activity"]'
        },
        'layout': {
            'sidebar_collapsed': False,
            'compact_mode': False
        }
    }
    
    current_user.settings = settings
    db.session.commit()
    flash('Dashboard settings have been reset to defaults!', 'success')
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Dashboard settings reset successfully'})
    
    return redirect(url_for('user.dashboard_settings'))

@user_bp.route('/dashboard_settings/widget_order', methods=['POST'])
@login_required
def update_widget_order():
    """Update widget order via AJAX."""
    widget_order = request.json.get('order', [])
    
    if not isinstance(widget_order, list):
        return jsonify({'success': False, 'message': 'Invalid widget order format'})
    
    settings = current_user.settings or {}
    if 'dashboard' not in settings:
        settings['dashboard'] = {}
    if 'widgets' not in settings['dashboard']:
        settings['dashboard']['widgets'] = {}
    
    settings['dashboard']['widgets']['order'] = str(widget_order)
    current_user.settings = settings
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Widget order updated successfully'})

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