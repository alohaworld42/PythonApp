from app import db
from datetime import datetime

class Purchase(db.Model):
    """Purchase model for storing user purchase information."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    store_name = db.Column(db.String(255), nullable=False)
    order_id = db.Column(db.String(255), nullable=True)
    is_shared = db.Column(db.Boolean, nullable=False, default=False)
    share_comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interactions = db.relationship('Interaction', backref='purchase', lazy=True)
    
    def __repr__(self):
        return f"Purchase('{self.product_id}', '{self.store_name}', '{self.purchase_date}')"