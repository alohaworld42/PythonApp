import re
import requests
import os
from flask import current_app
from urllib.parse import urlparse
from datetime import datetime
from app import db
from app.models.product import Product

# Standard category mapping
CATEGORY_MAPPING = {
    # Clothing & Accessories
    'clothing': 'Clothing',
    'apparel': 'Clothing',
    'fashion': 'Clothing',
    'shoes': 'Shoes',
    'footwear': 'Shoes',
    'accessories': 'Accessories',
    'jewelry': 'Accessories',
    'watches': 'Accessories',
    'bags': 'Accessories',
    'handbags': 'Accessories',
    
    # Electronics
    'electronics': 'Electronics',
    'computers': 'Electronics',
    'laptops': 'Electronics',
    'phones': 'Electronics',
    'mobile': 'Electronics',
    'tablets': 'Electronics',
    'cameras': 'Electronics',
    'audio': 'Electronics',
    'headphones': 'Electronics',
    'speakers': 'Electronics',
    'gaming': 'Electronics',
    
    # Home & Kitchen
    'home': 'Home',
    'kitchen': 'Home',
    'furniture': 'Home',
    'decor': 'Home',
    'appliances': 'Home',
    'garden': 'Home',
    'bedding': 'Home',
    'bath': 'Home',
    
    # Beauty & Personal Care
    'beauty': 'Beauty',
    'personal care': 'Beauty',
    'makeup': 'Beauty',
    'skincare': 'Beauty',
    'haircare': 'Beauty',
    'fragrance': 'Beauty',
    'perfume': 'Beauty',
    
    # Sports & Outdoors
    'sports': 'Sports',
    'outdoors': 'Sports',
    'fitness': 'Sports',
    'exercise': 'Sports',
    'camping': 'Sports',
    'hiking': 'Sports',
    
    # Books & Media
    'books': 'Books & Media',
    'ebooks': 'Books & Media',
    'music': 'Books & Media',
    'movies': 'Books & Media',
    'video': 'Books & Media',
    'games': 'Books & Media',
    
    # Toys & Kids
    'toys': 'Toys & Kids',
    'kids': 'Toys & Kids',
    'baby': 'Toys & Kids',
    
    # Food & Grocery
    'food': 'Food & Grocery',
    'grocery': 'Food & Grocery',
    'drinks': 'Food & Grocery',
    'beverages': 'Food & Grocery',
    'snacks': 'Food & Grocery',
    
    # Health & Wellness
    'health': 'Health & Wellness',
    'wellness': 'Health & Wellness',
    'vitamins': 'Health & Wellness',
    'supplements': 'Health & Wellness',
    'medical': 'Health & Wellness',
    
    # Other
    'other': 'Other',
    'miscellaneous': 'Other',
}

def normalize_category(category_string):
    """Normalize product category to a standard set."""
    if not category_string:
        return 'Other'
    
    # Convert to lowercase for matching
    category_lower = category_string.lower()
    
    # Try direct match first
    if category_lower in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[category_lower]
    
    # Try partial match
    for key, value in CATEGORY_MAPPING.items():
        if key in category_lower:
            return value
    
    # Default category
    return 'Other'

def normalize_price(price_value, currency='USD'):
    """Normalize price to a standard format."""
    if isinstance(price_value, (int, float)):
        return float(price_value)
    
    if isinstance(price_value, str):
        # Remove currency symbols and non-numeric characters
        price_str = re.sub(r'[^\d.]', '', price_value)
        try:
            return float(price_str)
        except ValueError:
            return 0.0
    
    return 0.0

def normalize_currency(currency_code):
    """Normalize currency code to standard 3-letter code."""
    if not currency_code:
        return 'USD'
    
    # Convert to uppercase
    currency = currency_code.upper()
    
    # List of valid currency codes
    valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CNY', 'INR']
    
    if currency in valid_currencies:
        return currency
    
    # Map common symbols to codes
    currency_map = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR'
    }
    
    if currency in currency_map:
        return currency_map[currency]
    
    # Default to USD
    return 'USD'

def download_and_save_image(image_url, product_id):
    """Download and save product image."""
    if not image_url:
        return None
    
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None
        
        # Parse URL to get file extension
        parsed_url = urlparse(image_url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.jpg'  # Default extension
        
        # Create filename
        filename = f"product_{product_id}{ext}"
        filepath = os.path.join(current_app.root_path, 'static', 'images', 'products', filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        # Return the relative path
        return f"images/products/{filename}"
    except Exception as e:
        current_app.logger.error(f"Error downloading image: {e}")
        return None

def normalize_product_data(product_data, source):
    """Normalize product data from different sources."""
    normalized = {}
    
    # Handle different source formats
    if source == 'shopify':
        normalized['title'] = product_data.get('title', '')
        normalized['description'] = product_data.get('body_html', '')
        normalized['price'] = normalize_price(product_data.get('variants', [{}])[0].get('price', 0))
        normalized['currency'] = normalize_currency(product_data.get('currency', 'USD'))
        
        # Get image URL
        if product_data.get('images') and len(product_data['images']) > 0:
            normalized['image_url'] = product_data['images'][0].get('src')
        else:
            normalized['image_url'] = None
        
        # Get category
        if product_data.get('product_type'):
            normalized['category'] = normalize_category(product_data['product_type'])
        else:
            normalized['category'] = 'Other'
        
        # Additional metadata
        normalized['metadata'] = {
            'vendor': product_data.get('vendor'),
            'tags': product_data.get('tags'),
            'variants': len(product_data.get('variants', [])),
            'created_at': product_data.get('created_at'),
            'updated_at': product_data.get('updated_at')
        }
    
    elif source == 'woocommerce':
        normalized['title'] = product_data.get('name', '')
        normalized['description'] = product_data.get('description', '')
        normalized['price'] = normalize_price(product_data.get('price', 0))
        normalized['currency'] = normalize_currency(product_data.get('currency', 'USD'))
        
        # Get image URL
        if product_data.get('images') and len(product_data['images']) > 0:
            normalized['image_url'] = product_data['images'][0].get('src')
        else:
            normalized['image_url'] = None
        
        # Get category
        categories = []
        for cat in product_data.get('categories', []):
            categories.append(cat.get('name', ''))
        
        if categories:
            normalized['category'] = normalize_category(', '.join(categories))
        else:
            normalized['category'] = 'Other'
        
        # Additional metadata
        normalized['metadata'] = {
            'sku': product_data.get('sku'),
            'tags': [tag['name'] for tag in product_data.get('tags', [])],
            'variations': len(product_data.get('variations', [])),
            'date_created': product_data.get('date_created'),
            'date_modified': product_data.get('date_modified')
        }
    
    else:
        # Generic normalization for unknown sources
        normalized['title'] = product_data.get('title', product_data.get('name', ''))
        normalized['description'] = product_data.get('description', '')
        normalized['price'] = normalize_price(product_data.get('price', 0))
        normalized['currency'] = normalize_currency(product_data.get('currency', 'USD'))
        normalized['image_url'] = product_data.get('image_url', product_data.get('image', None))
        normalized['category'] = normalize_category(product_data.get('category', ''))
        normalized['metadata'] = {}
    
    return normalized

def create_or_update_product(product_data, source, external_id=None):
    """Create or update a product in the database."""
    # Normalize the product data
    normalized = normalize_product_data(product_data, source)
    
    # Check if product exists
    if external_id:
        product = Product.query.filter_by(
            external_id=str(external_id),
            source=source
        ).first()
    else:
        product = None
    
    if not product:
        # Create new product
        product = Product(
            external_id=str(external_id) if external_id else None,
            source=source,
            title=normalized['title'],
            description=normalized['description'],
            price=normalized['price'],
            currency=normalized['currency'],
            category=normalized['category'],
            image_url=normalized['image_url'],
            product_metadata=normalized['metadata']
        )
        db.session.add(product)
    else:
        # Update existing product
        product.title = normalized['title']
        product.description = normalized['description']
        product.price = normalized['price']
        product.currency = normalized['currency']
        product.category = normalized['category']
        product.image_url = normalized['image_url']
        product.product_metadata = normalized['metadata']
    
    db.session.commit()
    
    # Download and save image if URL is provided
    if product.image_url and not product.image_url.startswith('images/products/'):
        local_image_path = download_and_save_image(product.image_url, product.id)
        if local_image_path:
            product.image_url = local_image_path
            db.session.commit()
    
    return product