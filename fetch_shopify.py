from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    shopify_customer_id = db.Column(db.String(255), nullable=True)
    # Add other fields as necessary, such as name, address, etc.

def fetch_products_from_shopify():
    """Fetches product data from Shopify."""
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/products.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['products']
    else:
        return []

def fetch_customer_from_shopify(email):
    """Fetch a customer's information from Shopify by email."""
    url = f"https://{SHOPIFY_SHOP_NAME}.myshopify.com/admin/api/2021-04/customers/search.json?query=email:{email}"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        customers = response.json().get('customers', [])
        if customers:
            return customers[0]  # Assuming the first customer is the match
    return None

def save_products(products):
    for product in products:
        new_product = Product(
            title=product['title'],
            description=product.get('body_html'),
            image_url=product['images'][0]['src'] if product['images'] else None
            # Map other fields accordingly
        )
    db.session.add(new_product)
    db.session.commit()

products = fetch_products_from_shopify()
save_products(products)

@app.route('/orders')
def orders():
    products = Product.query.all()
    return render_template('BuyRoll.html', products=products)