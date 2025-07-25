from app import db
from app.models.notification import Notification
from app.models.user import User
from app.models.purchase import Purchase

class NotificationService:
    """Service for managing user notifications."""
    
    @staticmethod
    def create_like_notification(purchase_id, liker_user_id):
        """Create a notification when someone likes a purchase."""
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return None
            
        # Don't notify if user likes their own purchase
        if purchase.user_id == liker_user_id:
            return None
            
        liker = User.query.get(liker_user_id)
        if not liker:
            return None
            
        # Check if notification already exists (to avoid duplicates)
        existing = Notification.query.filter_by(
            user_id=purchase.user_id,
            type='like',
            related_user_id=liker_user_id,
            related_purchase_id=purchase_id
        ).first()
        
        if existing:
            return existing
            
        notification = Notification(
            user_id=purchase.user_id,
            type='like',
            message=f"{liker.name} liked your purchase",
            related_user_id=liker_user_id,
            related_purchase_id=purchase_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def create_comment_notification(purchase_id, commenter_user_id, comment_content):
        """Create a notification when someone comments on a purchase."""
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            return None
            
        # Don't notify if user comments on their own purchase
        if purchase.user_id == commenter_user_id:
            return None
            
        commenter = User.query.get(commenter_user_id)
        if not commenter:
            return None
            
        notification = Notification(
            user_id=purchase.user_id,
            type='comment',
            message=f"{commenter.name} commented on your purchase",
            related_user_id=commenter_user_id,
            related_purchase_id=purchase_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def create_friend_request_notification(user_id, requester_user_id):
        """Create a notification when someone sends a friend request."""
        requester = User.query.get(requester_user_id)
        if not requester:
            return None
            
        # Check if notification already exists
        existing = Notification.query.filter_by(
            user_id=user_id,
            type='friend_request',
            related_user_id=requester_user_id
        ).first()
        
        if existing:
            return existing
            
        notification = Notification(
            user_id=user_id,
            type='friend_request',
            message=f"{requester.name} sent you a friend request",
            related_user_id=requester_user_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read."""
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=user_id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user."""
        notifications = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).all()
        
        for notification in notifications:
            notification.is_read = True
            
        db.session.commit()
        return len(notifications)
    
    @staticmethod
    def get_user_notifications(user_id, limit=20, unread_only=False):
        """Get notifications for a user."""
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
            
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        return notifications
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user."""
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()
    
    @staticmethod
    def delete_like_notification(purchase_id, liker_user_id):
        """Delete like notification when someone unlikes a purchase."""
        notification = Notification.query.filter_by(
            type='like',
            related_user_id=liker_user_id,
            related_purchase_id=purchase_id
        ).first()
        
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def create_new_purchase_notification(user_id, friend_user_id, purchase_id):
        """Create a notification when a friend shares a new purchase."""
        friend = User.query.get(friend_user_id)
        if not friend:
            return None
            
        notification = Notification(
            user_id=user_id,
            type='new_purchase',
            message=f"{friend.name} shared a new purchase",
            related_user_id=friend_user_id,
            related_purchase_id=purchase_id
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification