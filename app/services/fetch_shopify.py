import requests
import logging
import os
from dotenv import load_dotenv
from app.models import Product
from app import db

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHOPIFY_SHOP_NAME = os.getenv('SHOPIFY_SHOP_NAME')
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')
SHOPIFY_PASSWORD = os.getenv('SHOPIFY_PASSWORD')
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

def fetch_products_from_shopify():
    url = f'https://{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/2021-04/products.json'
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('products', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def save_products(products):
    for product in products:
        new_product = Product(
            title=product['title'],
            description=product.get('body_html'),
            image_url=product['images'][0]['src'] if product['images'] else None
        )
        db.session.add(new_product)
    db.session.commit()
