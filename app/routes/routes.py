from flask import request, jsonify, render_template, current_app as app
from .. import db
from ..models import Product, User
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.fetch_shopify import fetch_products_from_shopify, save_products

@app.route('/orders')
def orders():
    products = Product.query.all()
    return render_template('BuyRoll.html', products=products)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        with db.session.begin():
            db.session.execute("INSERT INTO user (username, password) VALUES (:username, :password)", 
                                {"username": username, "password": hashed_password})
        return jsonify({"success": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        user = db.session.execute("SELECT password FROM user WHERE username = :username", 
                                  {"username": username}).fetchone()
    except Exception as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    if user and check_password_hash(user[0], password):
        return jsonify({"success": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/fetch_shopify')
def fetch_shopify():
    products = fetch_products_from_shopify()
    if products:
        save_products(products)
        return jsonify({"success": "Products fetched and saved successfully"}), 200
    return jsonify({"error": "Failed to fetch products from Shopify"}), 500
