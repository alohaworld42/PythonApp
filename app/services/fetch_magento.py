import requests
import logging
import os
from dotenv import load_dotenv
from app.models import Product
from app import db

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAGENTO_BASE_URL = os.getenv('MAGENTO_BASE_URL')
MAGENTO_API_KEY = os.getenv('MAGENTO_API_KEY')

def fetch_products_from_magento():
    url = f'{MAGENTO_BASE_URL}/rest/V1/products?searchCriteria='
    headers = {
        "Authorization": f"Bearer {MAGENTO_API_KEY}",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def save_products(products):
    for product in products:
        new_product = Product(
            title=product['name'],
            description=product.get('custom_attributes', [{}])[0].get('value', ''),
            image_url=None  # Magento's product image handling may need more details
        )
        db.session.add(new_product)
    db.session.commit()
