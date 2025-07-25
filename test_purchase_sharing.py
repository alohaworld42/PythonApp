#!/usr/bin/env python3
"""
Test script for purchase sharing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.connection import Connection
from app.services.purchase_sharing_service import PurchaseSharingService

def test_purchase_sharing():
    """Test the purchase sharing functionality."""
    
    # Create test app
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        # Drop and recreate tables to ensure clean state
        db.drop_all()
        db.create_all()
        
        # Create test users
        user1 = User(
            email='user1@test.com',
            password_hash=User.hash_password('password123'),
            name='Test User 1'
        )
        user2 = User(
            email='user2@test.com',
            password_hash=User.hash_password('password123'),
            name='Test User 2'
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Create test product
        product = Product(
            external_id='test-product-1',
            source='shopify',
            title='Test Product',
            description='A test product',
            image_url='https://example.com/image.jpg',
            price=29.99,
            currency='USD',
            category='Electronics'
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Create test purchase
        purchase = Purchase(
            user_id=user1.id,
            product_id=product.id,
            store_name='Test Store',
            order_id='ORDER-123',
            is_shared=False
        )
        
        db.session.add(purchase)
        db.session.commit()
        
        # Create friendship between users
        connection = Connection(
            user_id=user1.id,
            friend_id=user2.id,
            status='accepted'
        )
        reverse_connection = Connection(
            user_id=user2.id,
            friend_id=user1.id,
            status='accepted'
        )
        
        db.session.add(connection)
        db.session.add(reverse_connection)
        db.session.commit()
        
        print("✅ Test data created successfully")
        
        # Test 1: Toggle sharing (share)
        result = PurchaseSharingService.toggle_sharing(
            purchase.id, 
            user1.id, 
            "This is a great product!"
        )
        
        assert result['success'] == True
        assert result['is_shared'] == True
        
        # Verify purchase is shared
        updated_purchase = Purchase.query.get(purchase.id)
        assert updated_purchase.is_shared == True
        assert updated_purchase.share_comment == "This is a great product!"
        
        print("✅ Test 1 passed: Purchase sharing toggle (share)")
        
        # Test 2: Get sharing stats
        stats = PurchaseSharingService.get_sharing_stats(user1.id)
        assert stats['total_purchases'] == 1
        assert stats['shared_purchases'] == 1
        assert stats['sharing_percentage'] == 100.0
        
        print("✅ Test 2 passed: Sharing statistics")
        
        # Test 3: Get user's shared purchases
        shared_purchases = PurchaseSharingService.get_user_shared_purchases(user1.id)
        assert len(shared_purchases) == 1
        assert shared_purchases[0].id == purchase.id
        
        print("✅ Test 3 passed: Get user shared purchases")
        
        # Test 4: Get friends' shared purchases
        friends_purchases = PurchaseSharingService.get_friends_shared_purchases(user2.id)
        assert len(friends_purchases) == 1
        assert friends_purchases[0].id == purchase.id
        
        print("✅ Test 4 passed: Get friends shared purchases")
        
        # Test 5: Update share comment
        result = PurchaseSharingService.update_share_comment(
            purchase.id,
            user1.id,
            "Updated comment about this product"
        )
        
        assert result['success'] == True
        
        updated_purchase = Purchase.query.get(purchase.id)
        assert updated_purchase.share_comment == "Updated comment about this product"
        
        print("✅ Test 5 passed: Update share comment")
        
        # Test 6: Check purchase visibility
        can_view = PurchaseSharingService.can_view_purchase(purchase.id, user2.id)
        assert can_view == True
        
        # Test non-friend cannot view
        user3 = User(
            email='user3@test.com',
            password_hash=User.hash_password('password123'),
            name='Test User 3'
        )
        db.session.add(user3)
        db.session.commit()
        
        can_view_non_friend = PurchaseSharingService.can_view_purchase(purchase.id, user3.id)
        assert can_view_non_friend == False
        
        print("✅ Test 6 passed: Purchase visibility controls")
        
        # Test 7: Toggle sharing (unshare)
        result = PurchaseSharingService.toggle_sharing(purchase.id, user1.id)
        
        assert result['success'] == True
        assert result['is_shared'] == False
        
        updated_purchase = Purchase.query.get(purchase.id)
        assert updated_purchase.is_shared == False
        assert updated_purchase.share_comment == None  # Comment should be cleared
        
        print("✅ Test 7 passed: Purchase sharing toggle (unshare)")
        
        # Test 8: Bulk sharing
        # Create another purchase
        purchase2 = Purchase(
            user_id=user1.id,
            product_id=product.id,
            store_name='Test Store 2',
            order_id='ORDER-456',
            is_shared=False
        )
        db.session.add(purchase2)
        db.session.commit()
        
        result = PurchaseSharingService.bulk_update_sharing(
            user1.id,
            [purchase.id, purchase2.id],
            True
        )
        
        assert result['success'] == True
        assert result['updated_count'] == 2
        
        # Verify both purchases are shared
        updated_purchase1 = Purchase.query.get(purchase.id)
        updated_purchase2 = Purchase.query.get(purchase2.id)
        assert updated_purchase1.is_shared == True
        assert updated_purchase2.is_shared == True
        
        print("✅ Test 8 passed: Bulk sharing update")
        
        print("\n🎉 All purchase sharing tests passed!")
        
        return True

if __name__ == '__main__':
    try:
        test_purchase_sharing()
        print("\n✅ Purchase sharing functionality is working correctly!")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)