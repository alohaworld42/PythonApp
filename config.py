import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or '3b1f45b0c645c4427a3b2a3e3e73c1ed3a3b2a3e3e73c1ed'
    
    # Site URL for email links
    SITE_URL = os.environ.get('SITE_URL') or 'http://localhost:5000'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///buyroll.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@buyroll.com'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    
    # API settings
    API_RATE_LIMIT = '100/hour'
    
    # E-commerce integration settings
    SHOPIFY_API_VERSION = '2023-01'
    SHOPIFY_API_KEY = os.environ.get('SHOPIFY_API_KEY')
    SHOPIFY_API_SECRET = os.environ.get('SHOPIFY_API_SECRET')
    
    WOOCOMMERCE_API_VERSION = 'wc/v3'
    
    # Social login settings
    GOOGLE_OAUTH_CREDENTIALS = {
        'id': os.environ.get('GOOGLE_CLIENT_ID', ''),
        'secret': os.environ.get('GOOGLE_CLIENT_SECRET', '')
    }
    
    FACEBOOK_OAUTH_CREDENTIALS = {
        'id': os.environ.get('FACEBOOK_CLIENT_ID', ''),
        'secret': os.environ.get('FACEBOOK_CLIENT_SECRET', '')
    }
    
    AMAZON_OAUTH_CREDENTIALS = {
        'id': os.environ.get('AMAZON_CLIENT_ID', ''),
        'secret': os.environ.get('AMAZON_CLIENT_SECRET', '')
    }
    
    # Scheduler settings
    SCHEDULER_API_ENABLED = False
    SCHEDULER_TIMEZONE = 'UTC'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TEMPLATES_AUTO_RELOAD = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SCHEDULER_API_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Use stronger security settings in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Use environment variables for all sensitive settings in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')