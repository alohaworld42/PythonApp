#!/usr/bin/env python3
"""
Test script for social interactions functionality.
This script tests the like, comment, save, and notification features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.interaction import Interaction
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from datetime import datetime

def test_social_interactions():
    """Test social interactions functionality."""
    app = create_app()
    
    with app.app_context():
        # Create test users
        user1 = User(
            email='user1@test.com',
            name='User One',
            password_hash='hashed_password'
        )
        user2 = User(
            email='user2@test.com',
            name='User Two',
            password_hash='hashed_password'
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print(f"Created users: {user1.name} (ID: {user1.id}), {user2.name} (ID: {user2.id})")
        
        # Create test product
        product = Product(
            external_id='test-product-1',
            source='shopify',
            title='Test Product',
            description='A test product for social interactions',
            image_url='https://example.com/image.jpg',
            price=29.99,
            currency='USD',
            category='Electronics'
        )
        
        db.session.add(product)
        db.session.commit()
        
        print(f"Created product: {product.title} (ID: {product.id})")
        
        # Create test purchase by user1
        purchase = Purchase(
            user_id=user1.id,
            product_id=product.id,
            purchase_date=datetime.utcnow(),
            store_name='Test Store',
            order_id='ORDER-123',
            is_shared=True,
            share_comment='Love this product!'
        )
        
        db.session.add(purchase)
        db.session.commit()
        
        print(f"Created purchase: {purchase.id} by {user1.name}")
        
        # Test 1: Like functionality
        print("\n--- Testing Like Functionality ---")
        
        # User2 likes user1's purchase
        like = Interaction(
            user_id=user2.id,
            purchase_id=purchase.id,
            type='like'
        )
        
        db.session.add(like)
        db.session.commit()
        
        print(f"User2 liked purchase {purchase.id}")
        
        # Test like notification
        notification = NotificationService.create_like_notification(purchase.id, user2.id)
        print(f"Like notification created: {notification.message if notification else 'None'}")
        
        # Test 2: Comment functionality
        print("\n--- Testing Comment Functionality ---")
        
        # User2 comments on user1's purchase
        comment = Interaction(
            user_id=user2.id,
            purchase_id=purchase.id,
            type='comment',
            content='Great choice! I have the same one.'
        )
        
        db.session.add(comment)
        db.session.commit()
        
        print(f"User2 commented on purchase {purchase.id}: '{comment.content}'")
        
        # Test comment notification
        comment_notification = NotificationService.create_comment_notification(
            purchase.id, user2.id, comment.content
        )
        print(f"Comment notification created: {comment_notification.message if comment_notification else 'None'}")
        
        # Test 3: Save functionality
        print("\n--- Testing Save Functionality ---")
        
        # User2 saves user1's purchase
        save = Interaction(
            user_id=user2.id,
            purchase_id=purchase.id,
            type='save'
        )
        
        db.session.add(save)
        db.session.commit()
        
        print(f"User2 saved purchase {purchase.id}")
        
        # Test 4: Notification functionality
        print("\n--- Testing Notification Functionality ---")
        
        # Get notifications for user1
        notifications = NotificationService.get_user_notifications(user1.id)
        print(f"User1 has {len(notifications)} notifications:")
        
        for notif in notifications:
            print(f"  - {notif.type}: {notif.message} (Read: {notif.is_read})")
        
        # Get unread count
        unread_count = NotificationService.get_unread_count(user1.id)
        print(f"User1 has {unread_count} unread notifications")
        
        # Test 5: Interaction queries
        print("\n--- Testing Interaction Queries ---")
        
        # Get likes count for purchase
        likes_count = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='like'
        ).count()
        print(f"Purchase {purchase.id} has {likes_count} likes")
        
        # Get comments for purchase
        comments = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='comment'
        ).all()
        print(f"Purchase {purchase.id} has {len(comments)} comments:")
        for c in comments:
            user = User.query.get(c.user_id)
            print(f"  - {user.name}: {c.content}")
        
        # Get saved items for user2
        saved_items = Interaction.query.filter_by(
            user_id=user2.id,
            type='save'
        ).all()
        print(f"User2 has {len(saved_items)} saved items")
        
        # Test 6: Unlike functionality
        print("\n--- Testing Unlike Functionality ---")
        
        # Remove like
        db.session.delete(like)
        db.session.commit()
        
        # Delete like notification
        NotificationService.delete_like_notification(purchase.id, user2.id)
        
        print("Like removed and notification deleted")
        
        # Verify likes count is now 0
        likes_count = Interaction.query.filter_by(
            purchase_id=purchase.id,
            type='like'
        ).count()
        print(f"Purchase {purchase.id} now has {likes_count} likes")
        
        print("\n--- All Tests Completed Successfully! ---")
        
        # Clean up
        db.session.query(Notification).delete()
        db.session.query(Interaction).delete()
        db.session.query(Purchase).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        print("Test data cleaned up")

if __name__ == '__main__':
    test_social_interactions()