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
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Load configuration
    if config_class is None:
        app.config.from_object('config.DevelopmentConfig')
    else:
        app.config.from_object(config_class)
    
    # Setup logging
    from app.utils.logging_config import setup_logging
    setup_logging(app)
    
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
    
    from app.routes.api_auth import api_auth_bp
    app.register_blueprint(api_auth_bp, url_prefix='/api')
    
    from app.routes.api_user_friends import api_user_friends_bp
    app.register_blueprint(api_user_friends_bp, url_prefix='/api')
    
    from app.routes.api_purchase_sharing import api_purchase_sharing_bp
    app.register_blueprint(api_purchase_sharing_bp, url_prefix='/api')
    
    from app.routes.api_analytics import api_analytics_bp
    app.register_blueprint(api_analytics_bp, url_prefix='/api')
    
    from app.routes.integrations import integrations_bp
    app.register_blueprint(integrations_bp, url_prefix='/integrations')
    
    # Setup monitoring endpoints
    from app.utils.monitoring import create_health_endpoint
    create_health_endpoint(app)
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers, register_api_error_handlers
    register_error_handlers(app)
    register_api_error_handlers(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Initialize performance monitoring
    from app.utils.performance_monitor import init_performance_monitoring
    init_performance_monitoring(app)
    
    # Initialize database optimizations
    from app.utils.database_optimization import DatabaseConnectionPool, optimize_sqlite_settings
    DatabaseConnectionPool.configure_pool(app)
    
    # Apply database optimizations in production
    if not app.config.get('TESTING', False):
        with app.app_context():
            optimize_sqlite_settings()
    
    # Initialize CLI commands
    from app.cli.performance import init_performance_cli
    init_performance_cli(app)
    
    # Initialize scheduler if not in testing mode
    if not app.config.get('TESTING', False):
        from app.utils.scheduler import init_scheduler
        init_scheduler(app)
    
    return app