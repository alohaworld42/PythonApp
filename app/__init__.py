import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Set login view
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')
    
    from app.routes.social import social_bp
    app.register_blueprint(social_bp, url_prefix='/social')
    
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.routes.integrations import integrations_bp
    app.register_blueprint(integrations_bp, url_prefix='/integrations')
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Initialize scheduler if not in testing mode
    if not app.config.get('TESTING', False):
        from app.utils.scheduler import init_scheduler
        init_scheduler(app)
    
    return app