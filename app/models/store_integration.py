from app import db
from datetime import datetime

class StoreIntegration(db.Model):
    """StoreIntegration model for storing e-commerce platform connections."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # e.g., 'shopify', 'woocommerce'
    store_url = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)  # Should be encrypted in production
    store_metadata = db.Column(db.JSON, nullable=True)  # Renamed from metadata to avoid conflict with SQLAlchemy
    last_sync = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"StoreIntegration('{self.user_id}', '{self.platform}', '{self.store_url}')"