from app import db
from app.models.purchase import Purchase
from app.models.user import User
from app.models.connection import Connection
from app.services.notification_service import NotificationService
from app.utils.cache import cached, invalidate_social_cache
from app.utils.performance_monitor import monitor_database_query
from datetime import datetime

class PurchaseSharingService:
    """Service for managing purchase sharing functionality."""
    
    @staticmethod
    def toggle_sharing(purchase_id, user_id, share_comment=None):
        """Toggle sharing status of a purchase."""
        purchase = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()
        if not purchase:
            return {'success': False, 'message': 'Purchase not found or access denied'}
        
        # Toggle sharing status
        purchase.is_shared = not purchase.is_shared
        purchase.updated_at = datetime.utcnow()
        
        # Update share comment if provided, or clear it when unsharing
        if share_comment is not None:
            purchase.share_comment = share_comment if purchase.is_shared else None
        elif not purchase.is_shared:
            # Clear comment when unsharing if no comment provided
            purchase.share_comment = None
        
        db.session.commit()
        
        # Invalidate cache for this user and their friends
        invalidate_social_cache(user_id)
        
        # Create notifications for friends if sharing
        if purchase.is_shared:
            PurchaseSharingService._notify_friends_of_new_share(purchase_id, user_id)
        
        return {
            'success': True, 
            'is_shared': purchase.is_shared,
            'message': 'Item shared with friends' if purchase.is_shared else 'Item no longer shared'
        }
    
    @staticmethod
    def update_share_comment(purchase_id, user_id, comment):
        """Update the share comment for a purchase."""
        purchase = Purchase.query.filter_by(id=purchase_id, user_id=user_id).first()
        if not purchase:
            return {'success': False, 'message': 'Purchase not found or access denied'}
        
        if not purchase.is_shared:
            return {'success': False, 'message': 'Cannot add comment to unshared item'}
        
        purchase.share_comment = comment
        purchase.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'success': True, 'message': 'Share comment updated'}
    
    @staticmethod
    @cached(ttl=300, key_prefix='social_user_shared_')
    @monitor_database_query('SELECT', 'purchase')
    def get_user_shared_purchases(user_id, limit=None):
        """Get all shared purchases for a user."""
        query = Purchase.query.filter_by(user_id=user_id, is_shared=True).order_by(Purchase.purchase_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    @cached(ttl=180, key_prefix='social_friends_feed_')
    @monitor_database_query('SELECT', 'purchase')
    def get_friends_shared_purchases(user_id, limit=None):
        """Get shared purchases from user's friends."""
        # Get friend IDs
        friend_connections = Connection.query.filter_by(
            user_id=user_id, 
            status='accepted'
        ).all()
        
        friend_ids = [conn.friend_id for conn in friend_connections]
        
        if not friend_ids:
            return []
        
        # Get shared purchases from friends
        query = Purchase.query.filter(
            Purchase.user_id.in_(friend_ids),
            Purchase.is_shared == True
        ).order_by(Purchase.purchase_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    @cached(ttl=600, key_prefix='social_sharing_stats_')
    @monitor_database_query('SELECT', 'purchase')
    def get_sharing_stats(user_id):
        """Get sharing statistics for a user."""
        total_purchases = Purchase.query.filter_by(user_id=user_id).count()
        shared_purchases = Purchase.query.filter_by(user_id=user_id, is_shared=True).count()
        
        return {
            'total_purchases': total_purchases,
            'shared_purchases': shared_purchases,
            'sharing_percentage': round((shared_purchases / total_purchases * 100) if total_purchases > 0 else 0, 1)
        }
    
    @staticmethod
    def can_view_purchase(purchase_id, viewer_id):
        """Check if a user can view a specific purchase."""
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return False
        
        # Owner can always view
        if purchase.user_id == viewer_id:
            return True
        
        # Only shared purchases can be viewed by others
        if not purchase.is_shared:
            return False
        
        # Check if viewer is friends with the purchase owner
        connection = Connection.query.filter_by(
            user_id=viewer_id,
            friend_id=purchase.user_id,
            status='accepted'
        ).first()
        
        return connection is not None
    
    @staticmethod
    def get_purchase_privacy_level(purchase_id):
        """Get privacy level for a purchase."""
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return 'private'
        
        if not purchase.is_shared:
            return 'private'
        
        # For now, all shared purchases are visible to friends
        # This can be extended to support more granular privacy levels
        return 'friends'
    
    @staticmethod
    def _notify_friends_of_new_share(purchase_id, user_id):
        """Notify friends when a user shares a new purchase."""
        # Get user's friends
        friend_connections = Connection.query.filter_by(
            user_id=user_id, 
            status='accepted'
        ).all()
        
        # Create notifications for friends who have enabled this notification type
        for connection in friend_connections:
            friend = User.query.get(connection.friend_id)
            if friend and friend.settings:
                notifications = friend.settings.get('notifications', {})
                app_notifications = notifications.get('app', {})
                
                # Check if friend wants to be notified of new purchases
                if app_notifications.get('new_friend_purchases', True):
                    NotificationService.create_new_purchase_notification(
                        friend.id, user_id, purchase_id
                    )
    
    @staticmethod
    def bulk_update_sharing(user_id, purchase_ids, is_shared):
        """Bulk update sharing status for multiple purchases."""
        purchases = Purchase.query.filter(
            Purchase.id.in_(purchase_ids),
            Purchase.user_id == user_id
        ).all()
        
        updated_count = 0
        for purchase in purchases:
            if purchase.is_shared != is_shared:
                purchase.is_shared = is_shared
                purchase.updated_at = datetime.utcnow()
                
                # Clear share comment if unsharing
                if not is_shared:
                    purchase.share_comment = None
                
                updated_count += 1
        
        db.session.commit()
        
        # Notify friends if sharing multiple items
        if is_shared and updated_count > 0:
            for purchase in purchases:
                if purchase.is_shared:
                    PurchaseSharingService._notify_friends_of_new_share(purchase.id, user_id)
        
        return {
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} items {"shared" if is_shared else "unshared"}'
        }