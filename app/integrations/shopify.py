import requests
import json
import hmac
import hashlib
import base64
import time
from urllib.parse import urlencode, quote_plus
from flask import current_app, url_for, request, redirect, session
from app import db
from app.models.store_integration import StoreIntegration
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.user import User
from datetime import datetime

class ShopifyClient:
    """Client for interacting with the Shopify API."""
    
    def __init__(self, store_url=None, api_key=None, api_secret=None, access_token=None):
        """Initialize the Shopify client."""
        self.store_url = store_url
        self.api_key = api_key or current_app.config.get('SHOPIFY_API_KEY')
        self.api_secret = api_secret or current_app.config.get('SHOPIFY_API_SECRET')
        self.access_token = access_token
        self.api_version = current_app.config.get('SHOPIFY_API_VERSION', '2023-01')
    
    def get_auth_url(self, shop, redirect_uri, scopes):
        """Get the authorization URL for OAuth flow."""
        state = self._generate_nonce()
        session['shopify_oauth_state'] = state
        
        query_params = {
            'client_id': self.api_key,
            'scope': scopes,
            'redirect_uri': redirect_uri,
            'state': state,
            'grant_options[]': 'per-user'
        }
        
        return f"https://{shop}/admin/oauth/authorize?{urlencode(query_params)}"
    
    def get_access_token(self, shop, code):
        """Exchange authorization code for access token."""
        url = f"https://{shop}/admin/oauth/access_token"
        payload = {
            'client_id': self.api_key,
            'client_secret': self.api_secret,
            'code': code
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            current_app.logger.error(f"Failed to get access token: {response.text}")
            return None
    
    def verify_webhook(self, data, hmac_header):
        """Verify that webhook request is from Shopify."""
        digest = hmac.new(
            self.api_secret.encode('utf-8'),
            data,
            hashlib.sha256
        ).digest()
        
        computed_hmac = base64.b64encode(digest).decode('utf-8')
        return hmac.compare_digest(computed_hmac, hmac_header)
    
    def _generate_nonce(self):
        """Generate a random nonce for OAuth state."""
        return hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()
    
    def _make_api_request(self, endpoint, method='GET', data=None, params=None):
        """Make a request to the Shopify API."""
        if not self.store_url or not self.access_token:
            raise ValueError("Store URL and access token are required")
        
        url = f"https://{self.store_url}/admin/api/{self.api_version}/{endpoint}"
        headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Shopify API request failed: {e}")
            return None
    
    def get_shop_info(self):
        """Get information about the shop."""
        return self._make_api_request('shop.json')
    
    def get_products(self, limit=50, page=1):
        """Get products from the shop."""
        params = {
            'limit': limit,
            'page': page
        }
        return self._make_api_request('products.json', params=params)
    
    def get_orders(self, limit=50, page=1, status='any', customer_email=None):
        """Get orders from the shop."""
        params = {
            'limit': limit,
            'page': page,
            'status': status
        }
        
        if customer_email:
            params['email'] = customer_email
        
        return self._make_api_request('orders.json', params=params)
    
    def get_customer_by_email(self, email):
        """Get customer by email."""
        params = {
            'query': f"email:{email}"
        }
        return self._make_api_request('customers/search.json', params=params)


def sync_shopify_orders(integration_id):
    """Sync orders from Shopify for a specific integration."""
    integration = StoreIntegration.query.get(integration_id)
    if not integration or integration.platform != 'shopify':
        current_app.logger.error(f"Invalid integration ID: {integration_id}")
        return False
    
    user = User.query.get(integration.user_id)
    if not user:
        current_app.logger.error(f"User not found for integration: {integration_id}")
        return False
    
    client = ShopifyClient(
        store_url=integration.store_url,
        access_token=integration.access_token
    )
    
    # Get orders for the user's email
    orders_data = client.get_orders(customer_email=user.email)
    if not orders_data or 'orders' not in orders_data:
        current_app.logger.error(f"Failed to get orders for integration: {integration_id}")
        return False
    
    orders = orders_data['orders']
    for order in orders:
        # Process each order
        order_id = order['id']
        order_name = order['name']
        
        # Check if order already exists
        existing_purchase = Purchase.query.filter_by(
            user_id=user.id,
            order_id=str(order_id),
            store_name=integration.store_url
        ).first()
        
        if existing_purchase:
            continue
        
        # Process line items
        for item in order['line_items']:
            # Check if product exists
            product = Product.query.filter_by(
                external_id=str(item['product_id']),
                source='shopify'
            ).first()
            
            if not product:
                # Create new product
                product = Product(
                    external_id=str(item['product_id']),
                    source='shopify',
                    title=item['title'],
                    description=item.get('name', ''),
                    price=float(item['price']),
                    currency=order['currency'],
                    category='',  # Shopify doesn't provide category in orders
                    product_metadata={}  # Using product_metadata instead of metadata
                )
                
                # Try to get product image
                try:
                    product_data = client._make_api_request(f"products/{item['product_id']}.json")
                    if product_data and 'product' in product_data and product_data['product']['images']:
                        product.image_url = product_data['product']['images'][0]['src']
                except Exception as e:
                    current_app.logger.error(f"Error fetching product image: {e}")
                
                db.session.add(product)
                db.session.commit()
            
            # Create purchase
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                purchase_date=datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')),
                store_name=integration.store_url,
                order_id=str(order_id),
                is_shared=False  # Default to not shared
            )
            
            db.session.add(purchase)
    
    # Update last sync time
    integration.last_sync = datetime.utcnow()
    db.session.commit()
    
    return True


def setup_shopify_webhooks(shop, access_token):
    """Set up webhooks for Shopify store."""
    client = ShopifyClient(store_url=shop, access_token=access_token)
    
    # Set up order creation webhook
    webhook_url = url_for('integrations.shopify_webhook', _external=True)
    
    webhook_data = {
        'webhook': {
            'topic': 'orders/create',
            'address': webhook_url,
            'format': 'json'
        }
    }
    
    response = client._make_api_request('webhooks.json', method='POST', data=webhook_data)
    if not response:
        current_app.logger.error("Failed to set up Shopify webhook")
        return False
    
    return True

def get_shopify_auth_url(shop, redirect_uri, scopes='read_orders,read_products'):
    """Get Shopify OAuth authorization URL."""
    client = ShopifyClient()
    return client.get_auth_url(shop, redirect_uri, scopes)

def get_shopify_access_token(shop, code):
    """Get Shopify access token from authorization code."""
    client = ShopifyClient()
    return client.get_access_token(shop, code)

def create_shopify_integration(user_id, shop, access_token):
    """Create a new Shopify integration for a user."""
    # Check if integration already exists
    existing_integration = StoreIntegration.query.filter_by(
        user_id=user_id,
        platform='shopify',
        store_url=shop
    ).first()
    
    if existing_integration:
        # Update existing integration
        existing_integration.access_token = access_token
        existing_integration.updated_at = datetime.utcnow()
        db.session.commit()
        return existing_integration
    
    # Create new integration
    integration = StoreIntegration(
        user_id=user_id,
        platform='shopify',
        store_url=shop,
        access_token=access_token,
        store_metadata={}
    )
    
    db.session.add(integration)
    db.session.commit()
    
    # Set up webhooks
    try:
        setup_shopify_webhooks(shop, access_token)
    except Exception as e:
        current_app.logger.error(f"Failed to set up webhooks: {e}")
    
    return integration