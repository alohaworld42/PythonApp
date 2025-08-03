"""
Database migration to add ProductImage table for high-quality image support
"""

from app import db
from app.models.product_image import ProductImage

def upgrade():
    """Create the product_images table."""
    db.create_all()
    print("✅ Created product_images table for high-quality image support")

def downgrade():
    """Drop the product_images table."""
    db.drop_all()
    print("❌ Dropped product_images table")

if __name__ == "__main__":
    upgrade()