"""
Error reporting system for BuyRoll application
"""
import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from flask import current_app, request, g
from app.utils.logging_config import app_logger

class ErrorReporter:
    """Centralized error reporting system"""
    
    @staticmethod
    def report_error(error, context=None, user_id=None, severity='medium'):
        """
        Report an error through multiple channels
        
        Args:
            error: The exception or error object
            context: Additional context about the error
            user_id: ID of the user who encountered the error
            severity: Error severity (low, medium, high, critical)
        """
        error_data = ErrorReporter._prepare_error_data(error, context, user_id, severity)
        
        # Log the error
        ErrorReporter._log_error(error_data)
        
        # Send email notification for high/critical errors
        if severity in ['high', 'critical']:
            ErrorReporter._send_email_notification(error_data)
        
        # Send to external monitoring service (if configured)
        ErrorReporter._send_to_monitoring_service(error_data)
        
        # Store in database for tracking
        ErrorReporter._store_error_record(error_data)
    
    @staticmethod
    def _prepare_error_data(error, context, user_id, severity):
        """Prepare error data for reporting"""
        import traceback
        
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'severity': severity,
            'context': context or {},
            'user_id': user_id,
            'traceback': traceback.format_exc() if hasattr(error, '__traceback__') else None,
            'request_data': ErrorReporter._get_request_data(),
            'environment': os.environ.get('FLASK_ENV', 'unknown'),
            'app_version': '1.0.0'  # This could be dynamic
        }
        
        return error_data
    
    @staticmethod
    def _get_request_data():
        """Extract relevant request data"""
        if not request:
            return None
        
        try:
            return {
                'url': request.url,
                'method': request.method,
                'endpoint': request.endpoint,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'referrer': request.referrer,
                'args': dict(request.args),
                'form_data': dict(request.form) if request.form else None,
                'json_data': request.get_json() if request.is_json else None,
                'headers': dict(request.headers)
            }
        except Exception:
            return {'error': 'Could not extract request data'}
    
    @staticmethod
    def _log_error(error_data):
        """Log error using the application logger"""
        app_logger.log_event(
            'ERROR',
            'error_report',
            f"Error reported: {error_data['error_type']} - {error_data['error_message']}",
            **error_data
        )
    
    @staticmethod
    def _send_email_notification(error_data):
        """Send email notification for critical errors"""
        try:
            # Get email configuration
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_port = current_app.config.get('MAIL_PORT', 587)
            mail_username = current_app.config.get('MAIL_USERNAME')
            mail_password = current_app.config.get('MAIL_PASSWORD')
            
            if not all([mail_server, mail_username, mail_password]):
                app_logger.log_event(
                    'WARNING',
                    'email_config_missing',
                    'Email configuration missing, cannot send error notification'
                )
                return
            
            # Prepare email
            msg = MimeMultipart()
            msg['From'] = mail_username
            msg['To'] = current_app.config.get('ERROR_NOTIFICATION_EMAIL', mail_username)
            msg['Subject'] = f"[BuyRoll] {error_data['severity'].upper()} Error: {error_data['error_type']}"
            
            # Email body
            body = ErrorReporter._format_error_email(error_data)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
            server.quit()
            
            app_logger.log_event(
                'INFO',
                'error_email_sent',
                f"Error notification email sent for {error_data['error_type']}"
            )
            
        except Exception as e:
            app_logger.log_error(
                e,
                context='email_notification_failed',
                original_error=error_data['error_type']
            )
    
    @staticmethod
    def _format_error_email(error_data):
        """Format error data for email notification"""
        return f"""
        <html>
        <body>
            <h2 style="color: #dc2626;">BuyRoll Error Report</h2>
            
            <div style="background-color: #fee2e2; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Error Details</h3>
                <p><strong>Type:</strong> {error_data['error_type']}</p>
                <p><strong>Message:</strong> {error_data['error_message']}</p>
                <p><strong>Severity:</strong> {error_data['severity'].upper()}</p>
                <p><strong>Timestamp:</strong> {error_data['timestamp']}</p>
                <p><strong>Environment:</strong> {error_data['environment']}</p>
            </div>
            
            {f'''
            <div style="background-color: #fef3c7; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>User Information</h3>
                <p><strong>User ID:</strong> {error_data['user_id']}</p>
            </div>
            ''' if error_data['user_id'] else ''}
            
            {f'''
            <div style="background-color: #e0f2fe; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Request Information</h3>
                <p><strong>URL:</strong> {error_data['request_data']['url']}</p>
                <p><strong>Method:</strong> {error_data['request_data']['method']}</p>
                <p><strong>IP Address:</strong> {error_data['request_data']['remote_addr']}</p>
                <p><strong>User Agent:</strong> {error_data['request_data']['user_agent']}</p>
            </div>
            ''' if error_data['request_data'] else ''}
            
            {f'''
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Context</h3>
                <pre style="white-space: pre-wrap;">{json.dumps(error_data['context'], indent=2)}</pre>
            </div>
            ''' if error_data['context'] else ''}
            
            {f'''
            <div style="background-color: #fef2f2; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Stack Trace</h3>
                <pre style="white-space: pre-wrap; font-size: 12px;">{error_data['traceback']}</pre>
            </div>
            ''' if error_data['traceback'] else ''}
            
            <p style="margin-top: 20px; color: #6b7280;">
                This error was automatically reported by the BuyRoll error monitoring system.
            </p>
        </body>
        </html>
        """
    
    @staticmethod
    def _send_to_monitoring_service(error_data):
        """Send error to external monitoring service (e.g., Sentry)"""
        try:
            sentry_dsn = current_app.config.get('SENTRY_DSN')
            if sentry_dsn:
                # This would integrate with Sentry or similar service
                # For now, just log that we would send it
                app_logger.log_event(
                    'INFO',
                    'monitoring_service',
                    f"Would send error to monitoring service: {error_data['error_type']}"
                )
        except Exception as e:
            app_logger.log_error(
                e,
                context='monitoring_service_failed',
                original_error=error_data['error_type']
            )
    
    @staticmethod
    def _store_error_record(error_data):
        """Store error record in database for tracking"""
        try:
            from app.models.error_log import ErrorLog
            from app import db
            
            error_log = ErrorLog(
                error_type=error_data['error_type'],
                error_message=error_data['error_message'],
                severity=error_data['severity'],
                user_id=error_data['user_id'],
                context=json.dumps(error_data['context']),
                request_data=json.dumps(error_data['request_data']),
                traceback=error_data['traceback'],
                environment=error_data['environment'],
                timestamp=datetime.fromisoformat(error_data['timestamp'])
            )
            
            db.session.add(error_log)
            db.session.commit()
            
        except Exception as e:
            # Don't let error storage failure break the application
            app_logger.log_error(
                e,
                context='error_storage_failed',
                original_error=error_data['error_type']
            )

class UserFeedbackCollector:
    """Collect user feedback about errors"""
    
    @staticmethod
    def collect_error_feedback(error_id, user_id, feedback_data):
        """Collect user feedback about an error"""
        try:
            from app.models.error_feedback import ErrorFeedback
            from app import db
            
            feedback = ErrorFeedback(
                error_id=error_id,
                user_id=user_id,
                feedback_type=feedback_data.get('type', 'general'),
                message=feedback_data.get('message'),
                steps_to_reproduce=feedback_data.get('steps'),
                expected_behavior=feedback_data.get('expected'),
                actual_behavior=feedback_data.get('actual'),
                browser_info=feedback_data.get('browser'),
                additional_info=json.dumps(feedback_data.get('additional', {}))
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            app_logger.log_event(
                'INFO',
                'user_feedback_collected',
                f"User feedback collected for error {error_id}",
                user_id=user_id,
                feedback_type=feedback_data.get('type')
            )
            
            return feedback.id
            
        except Exception as e:
            app_logger.log_error(
                e,
                context='feedback_collection_failed',
                error_id=error_id,
                user_id=user_id
            )
            return None

# Utility functions for easy error reporting
def report_error(error, context=None, severity='medium'):
    """Convenience function to report errors"""
    user_id = getattr(g, 'user_id', None) if hasattr(g, 'user_id') else None
    ErrorReporter.report_error(error, context, user_id, severity)

def report_critical_error(error, context=None):
    """Report a critical error"""
    report_error(error, context, severity='critical')

def report_user_error(error, user_id, context=None):
    """Report an error with specific user context"""
    ErrorReporter.report_error(error, context, user_id, severity='medium')

# Decorator for automatic error reporting
def auto_report_errors(severity='medium'):
    """Decorator to automatically report errors from functions"""
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                report_error(
                    e,
                    context={
                        'function': func.__name__,
                        'args': str(args)[:500],  # Limit length
                        'kwargs': str(kwargs)[:500]
                    },
                    severity=severity
                )
                raise
        
        return wrapper
    
    return decorator