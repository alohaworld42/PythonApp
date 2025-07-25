from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.services.purchase_sharing_service import PurchaseSharingService
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """User dashboard route."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Get user's dashboard settings
    user_settings = current_user.settings or {}
    dashboard_settings = user_settings.get('dashboard', {
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
    })
    
    # Get items per page from settings
    items_per_page = dashboard_settings.get('items_per_page', 12)
    
    # Get user's purchases for dashboard
    purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.purchase_date.desc()).limit(items_per_page).all()
    
    # Get sharing statistics
    stats = PurchaseSharingService.get_sharing_stats(current_user.id)
    shared_count = stats['shared_purchases']
    
    # Get friends count
    friends_count = Connection.query.filter_by(user_id=current_user.id, status='accepted').count()
    
    # Get monthly spending (current month)
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_purchases = Purchase.query.filter(
        Purchase.user_id == current_user.id,
        Purchase.purchase_date >= current_month_start
    ).all()
    monthly_spending = sum(float(p.product.price) for p in monthly_purchases if p.product)
    
    # Get friend activity (recent shared purchases from friends)
    friend_activity = PurchaseSharingService.get_friends_shared_purchases(current_user.id, limit=5)
    
    return render_template(
        'dashboard.html',
        purchases=purchases,
        shared_count=shared_count,
        friends_count=friends_count,
        monthly_spending=f"{monthly_spending:.2f}",
        friend_activity=friend_activity,
        dashboard_settings=dashboard_settings
    )

@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('about.html')