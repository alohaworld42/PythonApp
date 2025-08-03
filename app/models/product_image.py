from app import db
from datetime import datetime

class ProductImage(db.Model):
    """Model for storing multiple product images with different sizes and quality."""
    
    __tablename__ = 'product_images'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Image URLs for different sizes
    thumbnail_url = db.Column(db.String(500), nullable=True)  # Small thumbnail (150x150)
    medium_url = db.Column(db.String(500), nullable=True)     # Medium size (300x300)
    large_url = db.Column(db.String(500), nullable=True)      # Large size (600x600)
    full_url = db.Column(db.String(500), nullable=True)       # Full/original size
    
    # Image metadata
    alt_text = db.Column(db.String(255), nullable=True)
    image_order = db.Column(db.Integer, default=0)  # Order for displaying images
    is_primary = db.Column(db.Boolean, default=False)  # Primary product image
    
    # WooCommerce specific fields
    external_image_id = db.Column(db.String(100), nullable=True)  # WooCommerce image ID
    source_metadata = db.Column(db.JSON, nullable=True)  # Store original WooCommerce image data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f"ProductImage(product_id={self.product_id}, is_primary={self.is_primary}, order={self.image_order})"
    
    def get_best_quality_url(self, preferred_size='large'):
        """Get the best quality image URL available, with fallback options."""
        size_priority = {
            'thumbnail': ['thumbnail_url', 'medium_url', 'large_url', 'full_url'],
            'medium': ['medium_url', 'large_url', 'full_url', 'thumbnail_url'],
            'large': ['large_url', 'full_url', 'medium_url', 'thumbnail_url'],
            'full': ['full_url', 'large_url', 'medium_url', 'thumbnail_url']
        }
        
        urls_to_try = size_priority.get(preferred_size, size_priority['large'])
        
        for url_field in urls_to_try:
            url = getattr(self, url_field)
            if url:
                return url
        
        return None
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'thumbnail_url': self.thumbnail_url,
            'medium_url': self.medium_url,
            'large_url': self.large_url,
            'full_url': self.full_url,
            'alt_text': self.alt_text,
            'image_order': self.image_order,
            'is_primary': self.is_primary,
            'best_quality_url': self.get_best_quality_url('large')
        }