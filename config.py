import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '3b1f45b0c645c4427a3b2a3e3e73c1ed3a3b2a3e3e73c1ed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
