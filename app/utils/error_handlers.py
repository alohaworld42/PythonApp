"""
Global error handlers for the BuyRoll application
"""
import traceback
from flask import render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging_config import app_logger, security_logger

def register_error_handlers(app):
    """Register global error handlers with the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        app_logger.log_error(
            error,
            context='bad_request',
            url=request.url,
            method=request.method,
            user_agent=request.headers.get('User-Agent')
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Bad request',
                'error_code': 400
            }), 400
        
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors"""
        security_logger.log_security_event(
            'unauthorized_access_attempt',
            severity='medium',
            url=request.url,
            method=request.method,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error_code': 401
            }), 401
        
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors"""
        security_logger.log_security_event(
            'forbidden_access_attempt',
            severity='high',
            url=request.url,
            method=request.method,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Access forbidden',
                'error_code': 403
            }), 403
        
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        app_logger.log_event(
            'INFO',
            'page_not_found',
            f"404 error for {request.url}",
            url=request.url,
            method=request.method,
            referrer=request.referrer
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Resource not found',
                'error_code': 404
            }), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors"""
        app_logger.log_error(
            error,
            context='method_not_allowed',
            url=request.url,
            method=request.method,
            allowed_methods=error.valid_methods if hasattr(error, 'valid_methods') else None
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Method not allowed',
                'error_code': 405
            }), 405
        
        return render_template('errors/405.html'), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors"""
        app_logger.log_error(
            error,
            context='file_too_large',
            url=request.url,
            method=request.method,
            content_length=request.content_length
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'File too large',
                'error_code': 413
            }), 413
        
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests errors"""
        security_logger.log_security_event(
            'rate_limit_exceeded',
            severity='medium',
            url=request.url,
            method=request.method,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Rate limit exceeded',
                'error_code': 429,
                'retry_after': getattr(error, 'retry_after', 3600)
            }), 429
        
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error"""
        # Log the full traceback for debugging
        app_logger.log_error(
            error,
            context='internal_server_error',
            url=request.url,
            method=request.method,
            traceback=traceback.format_exc(),
            user_agent=request.headers.get('User-Agent')
        )
        
        # Rollback any pending database transactions
        try:
            from app import db
            db.session.rollback()
        except Exception:
            pass  # Ignore rollback errors
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Internal server error',
                'error_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """Handle 502 Bad Gateway errors"""
        app_logger.log_error(
            error,
            context='bad_gateway',
            url=request.url,
            method=request.method
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Bad gateway',
                'error_code': 502
            }), 502
        
        return render_template('errors/502.html'), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors"""
        app_logger.log_error(
            error,
            context='service_unavailable',
            url=request.url,
            method=request.method
        )
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Service temporarily unavailable',
                'error_code': 503
            }), 503
        
        return render_template('errors/503.html'), 503
    
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        """Handle database errors"""
        app_logger.log_error(
            error,
            context='database_error',
            url=request.url,
            method=request.method,
            error_type=type(error).__name__
        )
        
        # Rollback the session
        try:
            from app import db
            db.session.rollback()
        except Exception:
            pass
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'Database error occurred',
                'error_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def unhandled_exception(error):
        """Handle any unhandled exceptions"""
        # Log the full traceback
        app_logger.log_error(
            error,
            context='unhandled_exception',
            url=request.url,
            method=request.method,
            traceback=traceback.format_exc()
        )
        
        # Rollback any pending database transactions
        try:
            from app import db
            db.session.rollback()
        except Exception:
            pass
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred',
                'error_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500

class APIException(Exception):
    """Custom exception for API errors"""
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        result = {'success': False, 'message': self.message}
        if self.payload:
            result.update(self.payload)
        return result

class ValidationError(APIException):
    """Exception for validation errors"""
    
    def __init__(self, message, errors=None):
        super().__init__(message, status_code=422)
        self.errors = errors or []
    
    def to_dict(self):
        result = super().to_dict()
        result['errors'] = self.errors
        return result

class AuthenticationError(APIException):
    """Exception for authentication errors"""
    
    def __init__(self, message="Authentication required"):
        super().__init__(message, status_code=401)

class AuthorizationError(APIException):
    """Exception for authorization errors"""
    
    def __init__(self, message="Access forbidden"):
        super().__init__(message, status_code=403)

class ResourceNotFoundError(APIException):
    """Exception for resource not found errors"""
    
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class RateLimitError(APIException):
    """Exception for rate limit errors"""
    
    def __init__(self, message="Rate limit exceeded", retry_after=3600):
        super().__init__(message, status_code=429, payload={'retry_after': retry_after})

def register_api_error_handlers(app):
    """Register API-specific error handlers"""
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """Handle custom API exceptions"""
        app_logger.log_error(
            error,
            context='api_exception',
            url=request.url,
            method=request.method,
            status_code=error.status_code
        )
        
        return jsonify(error.to_dict()), error.status_code
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle validation errors"""
        app_logger.log_error(
            error,
            context='validation_error',
            url=request.url,
            method=request.method,
            errors=error.errors
        )
        
        return jsonify(error.to_dict()), error.status_code

# Utility functions for error handling
def handle_database_error(func):
    """Decorator to handle database errors in routes"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            from app import db
            db.session.rollback()
            app_logger.log_error(
                e,
                context='database_operation',
                function_name=func.__name__
            )
            raise APIException("Database error occurred", status_code=500)
    
    return wrapper

def validate_json_request(required_fields=None):
    """Decorator to validate JSON request data"""
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                raise ValidationError("Request must be JSON")
            
            data = request.get_json()
            if not data:
                raise ValidationError("Request body cannot be empty")
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    raise ValidationError(
                        "Missing required fields",
                        errors=[f"Field '{field}' is required" for field in missing_fields]
                    )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator