from app import db
from datetime import datetime

class Product(db.Model):
    """Product model for storing product information."""
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(50), nullable=False)  # e.g., 'shopify', 'woocommerce'
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    category = db.Column(db.String(100), nullable=True)
    product_metadata = db.Column(db.JSON, nullable=True)  # Renamed from metadata to avoid conflict
    
    # Relationships
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    
    def __repr__(self):
        return f"Product('{self.title}', '{self.source}', '{self.price} {self.currency}')"