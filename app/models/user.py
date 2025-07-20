from datetime import datetime, timedelta
from flask import current_app
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from app import db, login_manager, bcrypt

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User model for authentication and profile information."""
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True, default='default.jpg')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    settings = db.Column(db.JSON, nullable=True)
    
    # Relationships
    purchases = db.relationship('Purchase', backref='user', lazy=True)
    connections_initiated = db.relationship('Connection', 
                                          foreign_keys='Connection.user_id',
                                          backref='user', 
                                          lazy=True)
    connections_received = db.relationship('Connection', 
                                         foreign_keys='Connection.friend_id',
                                         backref='friend', 
                                         lazy=True)
    interactions = db.relationship('Interaction', backref='user', lazy=True)
    store_integrations = db.relationship('StoreIntegration', backref='user', lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a timed token for password reset."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token):
        """Verify a password reset token."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)
    
    @staticmethod
    def hash_password(password):
        """Hash a password."""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if password matches hash."""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"