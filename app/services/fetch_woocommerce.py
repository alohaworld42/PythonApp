import requests
import logging
import os
from dotenv import load_dotenv
from app.models import Product
from app import db

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WC_STORE_URL = os.getenv('WC_STORE_URL')
WC_CONSUMER_KEY = os.getenv('WC_CONSUMER_KEY')
WC_CONSUMER_SECRET = os.getenv('WC_CONSUMER_SECRET')

def fetch_products_from_woocommerce():
    url = f'{WC_STORE_URL}/wp-json/wc/v3/products'
    try:
        response = requests.get(url, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def save_products(products):
    for product in products:
        new_product = Product(
            title=product['name'],
            description=product.get('description'),
            image_url=product['images'][0]['src'] if product['images'] else None
        )
        db.session.add(new_product)
    db.session.commit()
