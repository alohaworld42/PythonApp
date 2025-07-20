from app import db
from datetime import datetime

class Interaction(db.Model):
    """Interaction model for storing user interactions with purchases."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'like', 'comment', 'save'
    content = db.Column(db.Text, nullable=True)  # For comments
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Interaction('{self.user_id}', '{self.purchase_id}', '{self.type}')"