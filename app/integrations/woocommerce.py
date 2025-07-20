import requests
import json
import time
import hmac
import hashlib
import base64
from urllib.parse import urlencode, quote_plus
from flask import current_app, url_for, request, redirect, session
from app import db
from app.models.store_integration import StoreIntegration
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.user import User
from datetime import datetime
from woocommerce import API

class WooCommerceClient:
    """Client for interacting with the WooCommerce API."""
    
    def __init__(self, store_url=None, consumer_key=None, consumer_secret=None):
        """Initialize the WooCommerce client."""
        self.store_url = store_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.api_version = current_app.config.get('WOOCOMMERCE_API_VERSION', 'wc/v3')
        
        if store_url and consumer_key and consumer_secret:
            self.wcapi = API(
                url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                version=self.api_version,
                wp_api=True,
                timeout=30
            )
        else:
            self.wcapi = None
    
    def verify_credentials(self):
        """Verify that the API credentials are valid."""
        try:
            response = self.wcapi.get("products", params={"per_page": 1})
            return response.status_code == 200
        except Exception as e:
            current_app.logger.error(f"WooCommerce API verification failed: {e}")
            return False
    
    def get_products(self, page=1, per_page=50):
        """Get products from the store."""
        try:
            response = self.wcapi.get("products", params={
                "page": page,
                "per_page": per_page
            })
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Failed to get products: {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Error getting products: {e}")
            return None
    
    def get_orders(self, page=1, per_page=50, customer_email=None):
        """Get orders from the store."""
        params = {
            "page": page,
            "per_page": per_page
        }
        
        if customer_email:
            params["customer"] = customer_email
        
        try:
            response = self.wcapi.get("orders", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Failed to get orders: {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Error getting orders: {e}")
            return None
    
    def get_customer_by_email(self, email):
        """Get customer by email."""
        try:
            response = self.wcapi.get("customers", params={
                "email": email
            })
            
            if response.status_code == 200:
                customers = response.json()
                if customers:
                    return customers[0]
                return None
            else:
                current_app.logger.error(f"Failed to get customer: {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Error getting customer: {e}")
            return None
    
    def get_product_by_id(self, product_id):
        """Get product details by ID."""
        try:
            response = self.wcapi.get(f"products/{product_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                current_app.logger.error(f"Failed to get product: {response.text}")
                return None
        except Exception as e:
            current_app.logger.error(f"Error getting product: {e}")
            return None


def sync_woocommerce_orders(integration_id):
    """Sync orders from WooCommerce for a specific integration."""
    integration = StoreIntegration.query.get(integration_id)
    if not integration or integration.platform != 'woocommerce':
        current_app.logger.error(f"Invalid integration ID: {integration_id}")
        return False
    
    user = User.query.get(integration.user_id)
    if not user:
        current_app.logger.error(f"User not found for integration: {integration_id}")
        return False
    
    # Parse metadata for credentials
    store_metadata = integration.store_metadata or {}
    consumer_key = store_metadata.get('consumer_key')
    consumer_secret = store_metadata.get('consumer_secret')
    
    if not consumer_key or not consumer_secret:
        current_app.logger.error(f"Missing WooCommerce credentials for integration: {integration_id}")
        return False
    
    client = WooCommerceClient(
        store_url=integration.store_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )
    
    # Get customer ID by email
    customer = client.get_customer_by_email(user.email)
    if not customer:
        current_app.logger.error(f"Customer not found for email: {user.email}")
        return False
    
    customer_id = customer['id']
    
    # Get orders for the customer
    orders = client.get_orders(customer=customer_id)
    if not orders:
        current_app.logger.error(f"Failed to get orders for integration: {integration_id}")
        return False
    
    for order in orders:
        order_id = order['id']
        
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
                source='woocommerce'
            ).first()
            
            if not product:
                # Get product details
                product_data = client.get_product_by_id(item['product_id'])
                
                if not product_data:
                    continue
                
                # Create new product
                product = Product(
                    external_id=str(item['product_id']),
                    source='woocommerce',
                    title=item['name'],
                    description=product_data.get('description', ''),
                    price=float(item['price']),
                    currency=order['currency'],
                    category=', '.join([cat['name'] for cat in product_data.get('categories', [])]),
                    product_metadata={},  # Using product_metadata instead of metadata
                    image_url=product_data['images'][0]['src'] if product_data.get('images') else None
                )
                
                db.session.add(product)
                db.session.commit()
            
            # Create purchase
            purchase_date = datetime.fromisoformat(order['date_created'].replace('Z', '+00:00'))
            purchase = Purchase(
                user_id=user.id,
                product_id=product.id,
                purchase_date=purchase_date,
                store_name=integration.store_url,
                order_id=str(order_id),
                is_shared=False  # Default to not shared
            )
            
            db.session.add(purchase)
    
    # Update last sync time
    integration.last_sync = datetime.utcnow()
    db.session.commit()
    
    return True


def setup_woocommerce_webhook(integration_id):
    """Set up webhook for WooCommerce store."""
    integration = StoreIntegration.query.get(integration_id)
    if not integration or integration.platform != 'woocommerce':
        current_app.logger.error(f"Invalid integration ID: {integration_id}")
        return False
    
    # Parse metadata for credentials
    store_metadata = integration.store_metadata or {}
    consumer_key = store_metadata.get('consumer_key')
    consumer_secret = store_metadata.get('consumer_secret')
    
    if not consumer_key or not consumer_secret:
        current_app.logger.error(f"Missing WooCommerce credentials for integration: {integration_id}")
        return False
    
    client = WooCommerceClient(
        store_url=integration.store_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret
    )
    
    # Set up order creation webhook
    webhook_url = url_for('integrations.woocommerce_webhook', _external=True)
    
    try:
        response = client.wcapi.post("webhooks", {
            "name": "BuyRoll Order Created",
            "topic": "order.created",
            "delivery_url": webhook_url
        })
        
        if response.status_code in (200, 201):
            # Store webhook ID in metadata
            store_metadata['webhook_id'] = response.json()['id']
            integration.store_metadata = store_metadata
            db.session.commit()
            return True
        else:
            current_app.logger.error(f"Failed to set up WooCommerce webhook: {response.text}")
            return False
    except Exception as e:
        current_app.logger.error(f"Error setting up WooCommerce webhook: {e}")
        return False