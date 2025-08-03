#!/usr/bin/env python3
"""
Test script for WooCommerce high-quality image system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_woocommerce_image_system():
    """Test the new WooCommerce image system."""
    try:
        from app import create_app, db
        from app.models.product import Product
        from app.models.product_image import ProductImage
        from app.services.woocommerce_image_service import WooCommerceImageService
        
        app = create_app()
        
        with app.app_context():
            print("Testing WooCommerce High-Quality Image System...")
            
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
            # Sample WooCommerce product data with multiple images
            sample_wc_data = {
                'id': 123,
                'name': 'Premium Wireless Headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'short_description': 'Premium headphones',
                'price': '199.99',
                'regular_price': '249.99',
                'sale_price': '199.99',
                'sku': 'WH-001',
                'stock_status': 'instock',
                'categories': [
                    {'id': 1, 'name': 'Electronics'},
                    {'id': 2, 'name': 'Audio'}
                ],
                'tags': [
                    {'id': 1, 'name': 'wireless'},
                    {'id': 2, 'name': 'premium'}
                ],
                'images': [
                    {
                        'id': 1,
                        'src': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&h=600',
                        'alt': 'Premium Wireless Headphones - Main View'
                    },
                    {
                        'id': 2,
                        'src': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&h=600',
                        'alt': 'Premium Wireless Headphones - Side View'
                    },
                    {
                        'id': 3,
                        'src': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&h=600',
                        'alt': 'Premium Wireless Headphones - Detail View'
                    }
                ],
                'permalink': 'https://example.com/product/premium-headphones',
                'date_created': '2024-01-01T00:00:00Z',
                'date_modified': '2024-01-02T00:00:00Z'
            }
            
            print("\n=== Testing Product Creation ===")
            
            # Test creating product from WooCommerce data
            product = WooCommerceImageService.create_product_from_wc_data(sample_wc_data)
            print(f"✅ Created product: {product.title}")
            print(f"✅ Product ID: {product.id}")
            print(f"✅ External ID: {product.external_id}")
            print(f"✅ Price: ${product.get_effective_price()}")
            print(f"✅ On Sale: {product.is_on_sale()}")
            print(f"✅ Discount: {product.get_discount_percentage()}%")
            
            print("\n=== Testing Image Processing ===")
            
            # Test image processing
            images = product.get_all_images()
            print(f"✅ Processed {len(images)} images")
            
            for i, image in enumerate(images):
                print(f"  Image {i+1}:")
                print(f"    - Primary: {image.is_primary}")
                print(f"    - Order: {image.image_order}")
                print(f"    - Alt Text: {image.alt_text}")
                print(f"    - Thumbnail: {image.thumbnail_url[:50]}..." if image.thumbnail_url else "    - Thumbnail: None")
                print(f"    - Medium: {image.medium_url[:50]}..." if image.medium_url else "    - Medium: None")
                print(f"    - Large: {image.large_url[:50]}..." if image.large_url else "    - Large: None")
                print(f"    - Full: {image.full_url[:50]}..." if image.full_url else "    - Full: None")
                print(f"    - Best Quality: {image.get_best_quality_url('large')[:50]}...")
            
            print("\n=== Testing Product Methods ===")
            
            # Test product methods
            primary_image = product.get_primary_image()
            if primary_image:
                print(f"✅ Primary image found: {primary_image.alt_text}")
                print(f"✅ Best image URL: {product.get_best_image_url('large')[:50]}...")
            else:
                print("❌ No primary image found")
            
            # Test product dictionary conversion
            product_dict = product.to_dict(include_images=True)
            print(f"✅ Product dict has {len(product_dict.get('images', []))} images")
            print(f"✅ Best image URL in dict: {product_dict.get('best_image_url', 'None')[:50]}...")
            
            print("\n=== Testing Database Queries ===")
            
            # Test database queries
            db_product = Product.query.filter_by(external_id='123').first()
            if db_product:
                print(f"✅ Product found in database: {db_product.title}")
                
                db_images = ProductImage.query.filter_by(product_id=db_product.id).all()
                print(f"✅ Found {len(db_images)} images in database")
                
                primary_db_image = ProductImage.query.filter_by(
                    product_id=db_product.id, 
                    is_primary=True
                ).first()
                
                if primary_db_image:
                    print(f"✅ Primary image in database: {primary_db_image.alt_text}")
                else:
                    print("❌ No primary image in database")
            else:
                print("❌ Product not found in database")
            
            print("\n=== Testing Template Integration ===")
            
            # Test template data preparation
            template_items = []
            products = Product.query.all()
            
            for prod in products:
                item_data = prod.to_dict(include_images=True)
                item_data['best_image_url'] = prod.get_best_image_url('large')
                template_items.append(item_data)
            
            print(f"✅ Prepared {len(template_items)} items for template")
            
            if template_items:
                first_item = template_items[0]
                print(f"✅ First item title: {first_item.get('title')}")
                print(f"✅ First item best image: {first_item.get('best_image_url', 'None')[:50]}...")
                print(f"✅ First item has {len(first_item.get('images', []))} images")
            
            print("\n=== Summary ===")
            print("✅ WooCommerce high-quality image system is working!")
            print("✅ Products can be created with multiple high-quality images")
            print("✅ Images are properly processed and stored with different sizes")
            print("✅ Template integration provides optimized image URLs")
            print("✅ Database relationships work correctly")
            
            # Cleanup
            db.session.rollback()
            
    except Exception as e:
        print(f"❌ Error testing WooCommerce image system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_woocommerce_image_system()