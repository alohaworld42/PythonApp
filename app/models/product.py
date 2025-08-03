from app import db
from datetime import datetime

class Product(db.Model):
    """Product model for storing product information."""
    
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(255), nullable=True)
    source = db.Column(db.String(50), nullable=False)  # e.g., 'shopify', 'woocommerce'
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    short_description = db.Column(db.Text, nullable=True)  # For WooCommerce short description
    
    # Keep legacy image_url for backward compatibility
    image_url = db.Column(db.String(255), nullable=True)
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False)
    regular_price = db.Column(db.Numeric(10, 2), nullable=True)  # Original price before discount
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)    # Discounted price
    currency = db.Column(db.String(3), nullable=False, default='USD')
    
    # Product details
    category = db.Column(db.String(100), nullable=True)
    categories = db.Column(db.JSON, nullable=True)  # Store multiple categories from WooCommerce
    tags = db.Column(db.JSON, nullable=True)        # Product tags
    sku = db.Column(db.String(100), nullable=True)  # Stock Keeping Unit
    
    # Stock and availability
    stock_status = db.Column(db.String(20), default='instock')  # instock, outofstock, onbackorder
    stock_quantity = db.Column(db.Integer, nullable=True)
    manage_stock = db.Column(db.Boolean, default=False)
    
    # Product attributes
    weight = db.Column(db.String(20), nullable=True)
    dimensions = db.Column(db.JSON, nullable=True)  # length, width, height
    
    # SEO and metadata
    slug = db.Column(db.String(255), nullable=True)
    permalink = db.Column(db.String(500), nullable=True)
    product_metadata = db.Column(db.JSON, nullable=True)  # Store additional WooCommerce data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    date_created = db.Column(db.DateTime, nullable=True)  # Original creation date from WooCommerce
    date_modified = db.Column(db.DateTime, nullable=True) # Last modification date from WooCommerce
    
    # Relationships
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    # images relationship is defined in ProductImage model
    
    def __repr__(self):
        return f"Product('{self.title}', '{self.source}', '{self.price} {self.currency}')"
    
    def get_primary_image(self):
        """Get the primary product image."""
        from app.models.product_image import ProductImage
        primary_image = ProductImage.query.filter_by(
            product_id=self.id, 
            is_primary=True
        ).first()
        
        if primary_image:
            return primary_image
        
        # Fallback to first image if no primary is set
        first_image = ProductImage.query.filter_by(
            product_id=self.id
        ).order_by(ProductImage.image_order).first()
        
        return first_image
    
    def get_all_images(self):
        """Get all product images ordered by image_order."""
        from app.models.product_image import ProductImage
        return ProductImage.query.filter_by(
            product_id=self.id
        ).order_by(ProductImage.image_order).all()
    
    def get_best_image_url(self, size='large'):
        """Get the best quality image URL for the product."""
        primary_image = self.get_primary_image()
        if primary_image:
            return primary_image.get_best_quality_url(size)
        
        # Fallback to legacy image_url
        return self.image_url
    
    def get_effective_price(self):
        """Get the effective selling price (sale price if available, otherwise regular price)."""
        if self.sale_price and self.sale_price > 0:
            return float(self.sale_price)
        return float(self.price)
    
    def get_discount_percentage(self):
        """Calculate discount percentage if on sale."""
        if self.sale_price and self.regular_price and self.sale_price < self.regular_price:
            discount = ((float(self.regular_price) - float(self.sale_price)) / float(self.regular_price)) * 100
            return round(discount)
        return 0
    
    def is_on_sale(self):
        """Check if product is currently on sale."""
        return self.sale_price and self.sale_price > 0 and self.sale_price < self.regular_price
    
    def to_dict(self, include_images=True):
        """Convert product to dictionary for API responses."""
        data = {
            'id': self.id,
            'external_id': self.external_id,
            'source': self.source,
            'title': self.title,
            'description': self.description,
            'short_description': self.short_description,
            'price': float(self.price),
            'regular_price': float(self.regular_price) if self.regular_price else None,
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'effective_price': self.get_effective_price(),
            'currency': self.currency,
            'category': self.category,
            'categories': self.categories,
            'tags': self.tags,
            'sku': self.sku,
            'stock_status': self.stock_status,
            'stock_quantity': self.stock_quantity,
            'is_on_sale': self.is_on_sale(),
            'discount_percentage': self.get_discount_percentage(),
            'permalink': self.permalink,
            'best_image_url': self.get_best_image_url(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_images:
            data['images'] = [img.to_dict() for img in self.get_all_images()]
        
        return data