"""
Logging configuration for BuyRoll application
"""
import os
import logging
import logging.handlers
from datetime import datetime
from flask import request, g
import json

def setup_logging(app):
    """Setup application logging configuration"""
    
    # Get log level from environment
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Console output
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Configure Flask app logger
    app.logger.setLevel(getattr(logging, log_level))
    
    # Add request logging
    @app.before_request
    def log_request_info():
        """Log incoming request information"""
        if not request.path.startswith('/static'):
            app.logger.info(
                f"Request: {request.method} {request.path} "
                f"from {request.remote_addr} "
                f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
            )
    
    @app.after_request
    def log_response_info(response):
        """Log response information"""
        if not request.path.startswith('/static'):
            app.logger.info(
                f"Response: {response.status_code} "
                f"for {request.method} {request.path}"
            )
        return response
    
    # Configure specific loggers
    configure_database_logging()
    configure_integration_logging()
    configure_security_logging()
    
    app.logger.info("Logging configuration completed")

def configure_database_logging():
    """Configure database-specific logging"""
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING)  # Only log warnings and errors

def configure_integration_logging():
    """Configure e-commerce integration logging"""
    integration_logger = logging.getLogger('buyroll.integrations')
    integration_logger.setLevel(logging.INFO)

def configure_security_logging():
    """Configure security-related logging"""
    security_logger = logging.getLogger('buyroll.security')
    security_logger.setLevel(logging.WARNING)

class StructuredLogger:
    """Structured logging utility for consistent log formatting"""
    
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
    
    def log_event(self, level, event_type, message, **kwargs):
        """Log a structured event"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'message': message,
            'user_id': getattr(g, 'user_id', None),
            'request_id': getattr(g, 'request_id', None),
            **kwargs
        }
        
        # Convert string level to integer if needed
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(level, json.dumps(log_data))
    
    def log_user_action(self, action, user_id, **kwargs):
        """Log user actions"""
        self.log_event(
            logging.INFO,
            'user_action',
            f"User {user_id} performed action: {action}",
            user_id=user_id,
            action=action,
            **kwargs
        )
    
    def log_integration_event(self, platform, event, **kwargs):
        """Log e-commerce integration events"""
        self.log_event(
            logging.INFO,
            'integration_event',
            f"{platform} integration: {event}",
            platform=platform,
            event=event,
            **kwargs
        )
    
    def log_security_event(self, event, severity='medium', **kwargs):
        """Log security-related events"""
        self.log_event(
            logging.WARNING,
            'security_event',
            f"Security event: {event}",
            event=event,
            severity=severity,
            **kwargs
        )
    
    def log_error(self, error, context=None, **kwargs):
        """Log application errors"""
        self.log_event(
            logging.ERROR,
            'application_error',
            f"Application error: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            **kwargs
        )

# Global structured logger instances
app_logger = StructuredLogger('buyroll.app')
security_logger = StructuredLogger('buyroll.security')
integration_logger = StructuredLogger('buyroll.integrations')

def log_performance(func):
    """Decorator to log function performance"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            app_logger.log_event(
                logging.INFO,
                'performance',
                f"Function {func.__name__} executed in {execution_time:.3f}s",
                function_name=func.__name__,
                execution_time=execution_time,
                success=True
            )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            
            app_logger.log_event(
                logging.ERROR,
                'performance',
                f"Function {func.__name__} failed after {execution_time:.3f}s: {str(e)}",
                function_name=func.__name__,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
            
            raise
    
    return wrapper