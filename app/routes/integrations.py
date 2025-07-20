from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.store_integration import StoreIntegration
from app.integrations.shopify import ShopifyClient, create_shopify_integration, get_shopify_auth_url, get_shopify_access_token
from app.integrations.woocommerce import WooCommerceClient, sync_woocommerce_orders, setup_woocommerce_webhook
from app.utils.scheduler import sync_integration
import json
from datetime import datetime

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/')
@login_required
def index():
    """Integrations dashboard."""
    integrations = StoreIntegration.query.filter_by(user_id=current_user.id).all()
    return render_template('integrations/connect.html', integrations=integrations)

@integrations_bp.route('/connect/shopify', methods=['GET', 'POST'])
@login_required
def connect_shopify():
    """Connect Shopify store."""
    if request.method == 'POST':
        shop = request.form.get('shop')
        if not shop:
            flash('Shop URL is required', 'danger')
            return redirect(url_for('integrations.connect_shopify'))
        
        # Normalize shop URL
        if not shop.startswith('https://'):
            shop = f"https://{shop}"
        
        if '.myshopify.com' not in shop:
            shop = f"{shop}.myshopify.com"
        
        # Check if integration already exists
        existing = StoreIntegration.query.filter_by(
            user_id=current_user.id,
            platform='shopify',
            store_url=shop
        ).first()
        
        if existing:
            flash('This Shopify store is already connected', 'warning')
            return redirect(url_for('integrations.index'))
        
        # Start OAuth flow
        client = ShopifyClient()
        redirect_uri = url_for('integrations.shopify_callback', _external=True)
        scopes = 'read_orders,read_products,read_customers'
        
        auth_url = client.get_auth_url(shop, redirect_uri, scopes)
        return redirect(auth_url)
    
    return render_template('integrations/connect_shopify.html')

@integrations_bp.route('/connect/shopify/callback')
@login_required
def shopify_callback():
    """Handle Shopify OAuth callback."""
    shop = request.args.get('shop')
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Verify state to prevent CSRF
    if state != session.get('shopify_oauth_state'):
        flash('Invalid state parameter', 'danger')
        return redirect(url_for('integrations.index'))
    
    if not shop or not code:
        flash('Missing required parameters', 'danger')
        return redirect(url_for('integrations.index'))
    
    # Exchange code for access token
    client = ShopifyClient()
    access_token = client.get_access_token(shop, code)
    
    if not access_token:
        flash('Failed to authenticate with Shopify', 'danger')
        return redirect(url_for('integrations.index'))
    
    # Create integration record
    integration = StoreIntegration(
        user_id=current_user.id,
        platform='shopify',
        store_url=shop,
        access_token=access_token,
        store_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(integration)
    db.session.commit()
    
    # No need to set up webhooks here as we're using a different approach
    
    # Trigger initial sync
    sync_integration(integration.id)
    
    flash('Shopify store connected successfully!', 'success')
    return redirect(url_for('integrations.index'))

@integrations_bp.route('/connect/woocommerce', methods=['GET', 'POST'])
@login_required
def connect_woocommerce():
    """Connect WooCommerce store."""
    if request.method == 'POST':
        store_url = request.form.get('store_url')
        consumer_key = request.form.get('consumer_key')
        consumer_secret = request.form.get('consumer_secret')
        
        if not store_url or not consumer_key or not consumer_secret:
            flash('All fields are required', 'danger')
            return redirect(url_for('integrations.connect_woocommerce'))
        
        # Normalize store URL
        if not store_url.startswith('http'):
            store_url = f"https://{store_url}"
        
        # Remove trailing slash
        store_url = store_url.rstrip('/')
        
        # Check if integration already exists
        existing = StoreIntegration.query.filter_by(
            user_id=current_user.id,
            platform='woocommerce',
            store_url=store_url
        ).first()
        
        if existing:
            flash('This WooCommerce store is already connected', 'warning')
            return redirect(url_for('integrations.index'))
        
        # Verify credentials
        client = WooCommerceClient(
            store_url=store_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret
        )
        
        if not client.verify_credentials():
            flash('Invalid WooCommerce credentials', 'danger')
            return redirect(url_for('integrations.connect_woocommerce'))
        
        # Create integration record
        integration = StoreIntegration(
            user_id=current_user.id,
            platform='woocommerce',
            store_url=store_url,
            access_token='',  # WooCommerce uses key/secret instead
            store_metadata={
                'consumer_key': consumer_key,
                'consumer_secret': consumer_secret
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(integration)
        db.session.commit()
        
        # Set up webhook
        setup_woocommerce_webhook(integration.id)
        
        # Trigger initial sync
        sync_integration(integration.id)
        
        flash('WooCommerce store connected successfully!', 'success')
        return redirect(url_for('integrations.index'))
    
    return render_template('integrations/connect_woocommerce.html')

@integrations_bp.route('/disconnect/<int:integration_id>', methods=['POST'])
@login_required
def disconnect(integration_id):
    """Disconnect a store integration."""
    integration = StoreIntegration.query.get_or_404(integration_id)
    
    if integration.user_id != current_user.id:
        flash('You do not have permission to disconnect this integration', 'danger')
        return redirect(url_for('integrations.index'))
    
    # TODO: Clean up webhooks if needed
    
    db.session.delete(integration)
    db.session.commit()
    
    flash('Store disconnected successfully', 'success')
    return redirect(url_for('integrations.index'))

@integrations_bp.route('/sync/<int:integration_id>', methods=['POST'])
@login_required
def sync(integration_id):
    """Manually sync a store integration."""
    integration = StoreIntegration.query.get_or_404(integration_id)
    
    if integration.user_id != current_user.id:
        flash('You do not have permission to sync this integration', 'danger')
        return redirect(url_for('integrations.index'))
    
    success = sync_integration(integration.id)
    
    if success:
        flash('Store synced successfully', 'success')
    else:
        flash('Failed to sync store', 'danger')
    
    return redirect(url_for('integrations.index'))

@integrations_bp.route('/webhook/shopify', methods=['POST'])
def shopify_webhook():
    """Handle Shopify webhooks."""
    # Verify webhook
    hmac_header = request.headers.get('X-Shopify-Hmac-Sha256')
    if not hmac_header:
        current_app.logger.error("Missing Shopify HMAC header")
        return '', 401
    
    data = request.get_data()
    shop_domain = request.headers.get('X-Shopify-Shop-Domain')
    
    # Find the integration for this shop
    integration = StoreIntegration.query.filter_by(
        platform='shopify',
        store_url=shop_domain
    ).first()
    
    if not integration:
        current_app.logger.error(f"No integration found for shop: {shop_domain}")
        return '', 404
    
    # Verify the webhook is from Shopify
    client = ShopifyClient(api_secret=current_app.config.get('SHOPIFY_API_SECRET'))
    if not client.verify_webhook(data, hmac_header):
        current_app.logger.error("Invalid Shopify webhook signature")
        return '', 401
    
    # Process the webhook
    try:
        webhook_data = json.loads(data)
        topic = request.headers.get('X-Shopify-Topic')
        
        if topic == 'orders/create':
            # Trigger a sync for this integration
            sync_integration(integration.id)
    except Exception as e:
        current_app.logger.error(f"Error processing Shopify webhook: {e}")
    
    return '', 200

@integrations_bp.route('/webhook/woocommerce', methods=['POST'])
def woocommerce_webhook():
    """Handle WooCommerce webhooks."""
    # WooCommerce webhooks include a signature in the X-WC-Webhook-Signature header
    signature = request.headers.get('X-WC-Webhook-Signature')
    if not signature:
        current_app.logger.error("Missing WooCommerce webhook signature")
        return '', 401
    
    data = request.get_data()
    source = request.headers.get('X-WC-Webhook-Source')
    
    # Find the integration for this source
    integration = StoreIntegration.query.filter_by(
        platform='woocommerce',
        store_url=source
    ).first()
    
    if not integration:
        current_app.logger.error(f"No integration found for source: {source}")
        return '', 404
    
    # Process the webhook
    try:
        webhook_data = json.loads(data)
        
        # Trigger a sync for this integration
        sync_integration(integration.id)
    except Exception as e:
        current_app.logger.error(f"Error processing WooCommerce webhook: {e}")
    
    return '', 200