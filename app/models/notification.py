from app import db
from datetime import datetime

class Notification(db.Model):
    """Notification model for storing user notifications."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'like', 'comment', 'friend_request'
    message = db.Column(db.String(255), nullable=False)
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # User who triggered the notification
    related_purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=True)  # Related purchase if applicable
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Notification('{self.user_id}', '{self.type}', '{self.message}')"
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'related_user_id': self.related_user_id,
            'related_purchase_id': self.related_purchase_id
        }