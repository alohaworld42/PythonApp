from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import current_user
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.services.purchase_sharing_service import PurchaseSharingService
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index_chakra.html')

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

@main_bp.route('/products')
def products():
    """Products page route with high-quality images."""
    # Get products from database with high-quality images
    from app.models.product import Product
    
    # Try to fetch products from database, fallback to sample data if there are issues
    items = []
    try:
        db_products = Product.query.limit(20).all()
        
        # Convert to template format with high-quality images
        for product in db_products:
            try:
                item_data = product.to_dict(include_images=True)
                # Add template-friendly fields
                item_data['best_image_url'] = product.get_best_image_url('large')
                items.append(item_data)
            except Exception:
                # Skip problematic products
                continue
    except Exception:
        # Database query failed, will use sample data below
        pass
    
    # If no products in database, use sample data with high-quality placeholders
    if not items:
        sample_items = [
            {
                'title': 'Premium Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'category': 'electronics',
                'image': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop&crop=center',
                'best_image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=400&fit=crop&crop=center',
                'url': '#',
                'price': 199.99,
                'regular_price': 249.99,
                'is_on_sale': True,
                'discount_percentage': 20
            },
            {
                'title': 'Designer Cotton T-Shirt',
                'description': 'Comfortable and stylish cotton t-shirt with modern design',
                'category': 'fashion',
                'image': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=400&fit=crop&crop=center',
                'best_image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=400&fit=crop&crop=center',
                'url': '#',
                'price': 29.99,
                'regular_price': 39.99,
                'is_on_sale': True,
                'discount_percentage': 25
            },
            {
                'title': 'Smart Coffee Maker',
                'description': 'WiFi-enabled coffee maker with app control',
                'category': 'home',
                'image': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&h=400&fit=crop&crop=center',
                'best_image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600&h=400&fit=crop&crop=center',
                'url': '#',
                'price': 149.99,
                'regular_price': 199.99,
                'is_on_sale': True,
                'discount_percentage': 25
            },
            {
                'title': 'Premium Yoga Mat',
                'description': 'Eco-friendly yoga mat with superior grip',
                'category': 'sports',
                'image': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=400&fit=crop&crop=center',
                'best_image_url': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=600&h=400&fit=crop&crop=center',
                'url': '#',
                'price': 39.99,
                'regular_price': 59.99,
                'is_on_sale': True,
                'discount_percentage': 33
            }
        ]
        items = sample_items
    
    return render_template('products_chakra.html', items=items)

@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('about.html')

@main_bp.route('/favicon.ico')
def favicon():
    """Serve favicon."""
    return send_from_directory(current_app.static_folder, 'images/logo.svg', mimetype='image/svg+xml')

@main_bp.route('/css-showcase')
def css_showcase():
    """CSS Architecture showcase page."""
    return render_template('css-showcase.html')

@main_bp.route('/components-showcase')
def components_showcase():
    """Component library showcase page."""
    return render_template('components-showcase.html')