from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from services.fetch_shopify import fetch_products_from_shopify, save_products as save_shopify_products
from services.fetch_woocommerce import fetch_products_from_woocommerce, save_products as save_woocommerce_products
from services.fetch_magento import fetch_products_from_magento, save_products as save_magento_products

data_integration = Blueprint('data_integration', __name__)

@data_integration.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@data_integration.route('/fetch_shopify')
@login_required
def fetch_shopify():
    products = fetch_products_from_shopify()
    if products:
        save_shopify_products(products)
        return jsonify({"success": "Products fetched and saved successfully"}), 200
    return jsonify({"error": "Failed to fetch products from Shopify"}), 500

@data_integration.route('/fetch_woocommerce')
@login_required
def fetch_woocommerce():
    products = fetch_products_from_woocommerce()
    if products:
        save_woocommerce_products(products)
        return jsonify({"success": "Products fetched and saved successfully"}), 200
    return jsonify({"error": "Failed to fetch products from WooCommerce"}), 500

@data_integration.route('/fetch_magento')
@login_required
def fetch_magento():
    products = fetch_products_from_magento()
    if products:
        save_magento_products(products)
        return jsonify({"success": "Products fetched and saved successfully"}), 200
    return jsonify({"error": "Failed to fetch products from Magento"}), 500
