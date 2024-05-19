import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
