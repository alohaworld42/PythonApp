"""
WooCommerce Image Service for handling high-quality product images
"""

import requests
import logging
from typing import List, Dict, Optional
from app import db
from app.models.product import Product
from app.models.product_image import ProductImage
from datetime import datetime

logger = logging.getLogger(__name__)

class WooCommerceImageService:
    """Service for processing and storing WooCommerce product images."""
    
    @staticmethod
    def process_product_images(product: Product, wc_product_data: Dict) -> List[ProductImage]:
        """
        Process and store images from WooCommerce product data.
        
        Args:
            product: The Product instance to associate images with
            wc_product_data: Raw product data from WooCommerce API
            
        Returns:
            List of created ProductImage instances
        """
        images_data = wc_product_data.get('images', [])
        if not images_data:
            logger.warning(f"No images found for product {product.id}")
            return []
        
        # Remove existing images for this product
        ProductImage.query.filter_by(product_id=product.id).delete()
        
        created_images = []
        
        for index, image_data in enumerate(images_data):
            try:
                product_image = WooCommerceImageService._create_product_image(
                    product, image_data, index
                )
                if product_image:
                    created_images.append(product_image)
                    
            except Exception as e:
                logger.error(f"Error processing image {index} for product {product.id}: {e}")
                continue
        
        # Set the first image as primary if no primary is set
        if created_images and not any(img.is_primary for img in created_images):
            created_images[0].is_primary = True
        
        db.session.commit()
        logger.info(f"Processed {len(created_images)} images for product {product.id}")
        
        return created_images
    
    @staticmethod
    def _create_product_image(product: Product, image_data: Dict, order: int) -> Optional[ProductImage]:
        """
        Create a ProductImage instance from WooCommerce image data.
        
        Args:
            product: The Product instance
            image_data: Single image data from WooCommerce
            order: Order/position of the image
            
        Returns:
            ProductImage instance or None if creation failed
        """
        try:
            # Extract image URLs - WooCommerce provides the main image URL
            # and we need to construct different sizes
            main_url = image_data.get('src', '')
            if not main_url:
                logger.warning(f"No src URL found in image data: {image_data}")
                return None
            
            # WooCommerce image size variations
            # The main URL is typically the full size
            full_url = main_url
            
            # Generate different size URLs based on WooCommerce naming conventions
            # WooCommerce typically uses suffixes like -150x150, -300x300, -600x600
            base_url = main_url.rsplit('.', 1)[0]  # Remove file extension
            extension = main_url.rsplit('.', 1)[1] if '.' in main_url else 'jpg'
            
            # Common WooCommerce image sizes
            thumbnail_url = f"{base_url}-150x150.{extension}"
            medium_url = f"{base_url}-300x300.{extension}"
            large_url = f"{base_url}-600x600.{extension}"
            
            # Verify if generated URLs exist, fallback to main URL if not
            thumbnail_url = WooCommerceImageService._verify_image_url(thumbnail_url, main_url)
            medium_url = WooCommerceImageService._verify_image_url(medium_url, main_url)
            large_url = WooCommerceImageService._verify_image_url(large_url, main_url)
            
            # Create ProductImage instance
            product_image = ProductImage(
                product_id=product.id,
                thumbnail_url=thumbnail_url,
                medium_url=medium_url,
                large_url=large_url,
                full_url=full_url,
                alt_text=image_data.get('alt', product.title),
                image_order=order,
                is_primary=(order == 0),  # First image is primary
                external_image_id=str(image_data.get('id', '')),
                source_metadata=image_data  # Store original WooCommerce data
            )
            
            db.session.add(product_image)
            
            logger.debug(f"Created ProductImage for product {product.id}, order {order}")
            return product_image
            
        except Exception as e:
            logger.error(f"Error creating ProductImage: {e}")
            return None
    
    @staticmethod
    def _verify_image_url(url: str, fallback_url: str) -> str:
        """
        Verify if an image URL exists, return fallback if not.
        
        Args:
            url: URL to verify
            fallback_url: Fallback URL if verification fails
            
        Returns:
            Verified URL or fallback URL
        """
        try:
            # Quick HEAD request to check if image exists
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                return url
            else:
                logger.debug(f"Image URL not found: {url}, using fallback")
                return fallback_url
                
        except requests.RequestException:
            logger.debug(f"Error verifying image URL: {url}, using fallback")
            return fallback_url
    
    @staticmethod
    def update_product_with_wc_data(product: Product, wc_product_data: Dict) -> Product:
        """
        Update product with comprehensive WooCommerce data including images.
        
        Args:
            product: Existing Product instance
            wc_product_data: Complete WooCommerce product data
            
        Returns:
            Updated Product instance
        """
        try:
            # Update basic product information
            product.title = wc_product_data.get('name', product.title)
            product.description = wc_product_data.get('description', product.description)
            product.short_description = wc_product_data.get('short_description', '')
            product.slug = wc_product_data.get('slug', '')
            product.permalink = wc_product_data.get('permalink', '')
            product.sku = wc_product_data.get('sku', '')
            
            # Update pricing
            product.price = float(wc_product_data.get('price', 0))
            product.regular_price = float(wc_product_data.get('regular_price', 0)) if wc_product_data.get('regular_price') else None
            product.sale_price = float(wc_product_data.get('sale_price', 0)) if wc_product_data.get('sale_price') else None
            
            # Update stock information
            product.stock_status = wc_product_data.get('stock_status', 'instock')
            product.stock_quantity = wc_product_data.get('stock_quantity')
            product.manage_stock = wc_product_data.get('manage_stock', False)
            
            # Update categories and tags
            categories = wc_product_data.get('categories', [])
            if categories:
                product.category = categories[0].get('name', '')
                product.categories = [cat.get('name') for cat in categories]
            
            tags = wc_product_data.get('tags', [])
            if tags:
                product.tags = [tag.get('name') for tag in tags]
            
            # Update dimensions and weight
            product.weight = wc_product_data.get('weight', '')
            dimensions = wc_product_data.get('dimensions', {})
            if dimensions:
                product.dimensions = {
                    'length': dimensions.get('length', ''),
                    'width': dimensions.get('width', ''),
                    'height': dimensions.get('height', '')
                }
            
            # Update timestamps
            if wc_product_data.get('date_created'):
                product.date_created = datetime.fromisoformat(
                    wc_product_data['date_created'].replace('Z', '+00:00')
                )
            
            if wc_product_data.get('date_modified'):
                product.date_modified = datetime.fromisoformat(
                    wc_product_data['date_modified'].replace('Z', '+00:00')
                )
            
            # Store complete metadata
            product.product_metadata = wc_product_data
            
            # Update legacy image_url for backward compatibility
            images = wc_product_data.get('images', [])
            if images:
                product.image_url = images[0].get('src', '')
            
            product.updated_at = datetime.utcnow()
            
            # Process and store high-quality images
            WooCommerceImageService.process_product_images(product, wc_product_data)
            
            logger.info(f"Updated product {product.id} with WooCommerce data")
            return product
            
        except Exception as e:
            logger.error(f"Error updating product {product.id} with WooCommerce data: {e}")
            raise
    
    @staticmethod
    def create_product_from_wc_data(wc_product_data: Dict, source: str = 'woocommerce') -> Product:
        """
        Create a new Product from WooCommerce data.
        
        Args:
            wc_product_data: Complete WooCommerce product data
            source: Source identifier (default: 'woocommerce')
            
        Returns:
            New Product instance
        """
        try:
            # Create basic product
            product = Product(
                external_id=str(wc_product_data.get('id', '')),
                source=source,
                title=wc_product_data.get('name', 'Untitled Product'),
                description=wc_product_data.get('description', ''),
                price=float(wc_product_data.get('price', 0)),
                currency='USD'  # Default, should be configurable
            )
            
            db.session.add(product)
            db.session.flush()  # Get the product ID
            
            # Update with complete WooCommerce data
            product = WooCommerceImageService.update_product_with_wc_data(product, wc_product_data)
            
            db.session.commit()
            
            logger.info(f"Created new product {product.id} from WooCommerce data")
            return product
            
        except Exception as e:
            logger.error(f"Error creating product from WooCommerce data: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def get_optimized_image_url(product: Product, size: str = 'large', format: str = 'webp') -> Optional[str]:
        """
        Get optimized image URL for a product with optional format conversion.
        
        Args:
            product: Product instance
            size: Desired image size ('thumbnail', 'medium', 'large', 'full')
            format: Desired image format ('webp', 'jpg', 'png')
            
        Returns:
            Optimized image URL or None
        """
        primary_image = product.get_primary_image()
        if not primary_image:
            return product.image_url  # Fallback to legacy
        
        base_url = primary_image.get_best_quality_url(size)
        if not base_url:
            return None
        
        # If WebP is requested and supported, try to convert URL
        if format == 'webp' and not base_url.endswith('.webp'):
            # This would require additional image processing service
            # For now, return the original URL
            pass
        
        return base_url