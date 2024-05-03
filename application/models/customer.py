from application import db


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    shopify_customer_id = db.Column(db.String(255), nullable=True)

    # Add other fields as necessary, such as name, address, etc.

    def __init__(self, email: str, shopify_customer_id: str):
        self.email = email
        self.shopify_customer_id = shopify_customer_id

    def __repr__(self):
        return {'id': self.id,
                'email': self.email,
                'shopify_customer_id': self.shopify_customer_id}
