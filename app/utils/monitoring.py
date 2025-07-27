"""
Application monitoring and health check utilities
"""
import os
import time
import psutil
from datetime import datetime, timedelta
from flask import jsonify, current_app
from app.models import User, Purchase, Connection
from app import db

class HealthChecker:
    """Application health monitoring"""
    
    @staticmethod
    def check_database():
        """Check database connectivity and basic operations"""
        try:
            # Test basic query
            user_count = User.query.count()
            return {
                'status': 'healthy',
                'user_count': user_count,
                'response_time': 'fast'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def check_disk_space():
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            
            status = 'healthy'
            if free_percent < 10:
                status = 'critical'
            elif free_percent < 20:
                status = 'warning'
            
            return {
                'status': status,
                'free_space_percent': round(free_percent, 2),
                'free_space_gb': round(disk_usage.free / (1024**3), 2),
                'total_space_gb': round(disk_usage.total / (1024**3), 2)
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    @staticmethod
    def check_memory():
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            if memory.percent > 90:
                status = 'critical'
            elif memory.percent > 80:
                status = 'warning'
            
            return {
                'status': status,
                'used_percent': memory.percent,
                'available_gb': round(memory.available / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2)
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'error': str(e)
            }
    
    @staticmethod
    def check_integrations():
        """Check e-commerce integration health"""
        # This would check if external APIs are responding
        # For now, return a placeholder
        return {
            'shopify': {'status': 'healthy', 'last_sync': '2024-01-01T00:00:00Z'},
            'woocommerce': {'status': 'healthy', 'last_sync': '2024-01-01T00:00:00Z'}
        }
    
    @classmethod
    def get_health_status(cls):
        """Get comprehensive health status"""
        health_checks = {
            'database': cls.check_database(),
            'disk_space': cls.check_disk_space(),
            'memory': cls.check_memory(),
            'integrations': cls.check_integrations(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Determine overall status
        overall_status = 'healthy'
        for check_name, check_result in health_checks.items():
            if check_name == 'timestamp':
                continue
            
            if isinstance(check_result, dict):
                if check_result.get('status') == 'critical':
                    overall_status = 'critical'
                    break
                elif check_result.get('status') == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
        
        health_checks['overall_status'] = overall_status
        return health_checks

class MetricsCollector:
    """Application metrics collection"""
    
    @staticmethod
    def get_user_metrics():
        """Get user-related metrics"""
        try:
            total_users = User.query.count()
            
            # Users registered in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            new_users_24h = User.query.filter(User.created_at >= yesterday).count()
            
            # Users logged in in last 24 hours
            active_users_24h = User.query.filter(User.last_login >= yesterday).count()
            
            return {
                'total_users': total_users,
                'new_users_24h': new_users_24h,
                'active_users_24h': active_users_24h
            }
        except Exception as e:
            current_app.logger.error(f"Error collecting user metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_purchase_metrics():
        """Get purchase-related metrics"""
        try:
            total_purchases = Purchase.query.count()
            shared_purchases = Purchase.query.filter(Purchase.is_shared == True).count()
            
            # Purchases in last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_purchases = Purchase.query.filter(Purchase.created_at >= yesterday).count()
            
            return {
                'total_purchases': total_purchases,
                'shared_purchases': shared_purchases,
                'recent_purchases_24h': recent_purchases,
                'sharing_rate': round((shared_purchases / total_purchases * 100), 2) if total_purchases > 0 else 0
            }
        except Exception as e:
            current_app.logger.error(f"Error collecting purchase metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_social_metrics():
        """Get social interaction metrics"""
        try:
            total_connections = Connection.query.filter(Connection.status == 'accepted').count()
            pending_requests = Connection.query.filter(Connection.status == 'pending').count()
            
            return {
                'total_connections': total_connections,
                'pending_requests': pending_requests
            }
        except Exception as e:
            current_app.logger.error(f"Error collecting social metrics: {str(e)}")
            return {}
    
    @staticmethod
    def get_system_metrics():
        """Get system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': round((disk.used / disk.total) * 100, 2),
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            current_app.logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    @classmethod
    def get_all_metrics(cls):
        """Get all application metrics"""
        return {
            'users': cls.get_user_metrics(),
            'purchases': cls.get_purchase_metrics(),
            'social': cls.get_social_metrics(),
            'system': cls.get_system_metrics(),
            'timestamp': datetime.utcnow().isoformat()
        }

def create_health_endpoint(app):
    """Create health check endpoint"""
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        health_status = HealthChecker.get_health_status()
        
        status_code = 200
        if health_status['overall_status'] == 'critical':
            status_code = 503
        elif health_status['overall_status'] == 'warning':
            status_code = 200  # Still operational
        
        return jsonify(health_status), status_code
    
    @app.route('/metrics')
    def metrics():
        """Metrics endpoint"""
        try:
            metrics_data = MetricsCollector.get_all_metrics()
            return jsonify(metrics_data)
        except Exception as e:
            current_app.logger.error(f"Error in metrics endpoint: {str(e)}")
            return jsonify({'error': 'Failed to collect metrics'}), 500
    
    @app.route('/status')
    def status():
        """Simple status endpoint"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })

class AlertManager:
    """Alert management for critical issues"""
    
    @staticmethod
    def check_and_alert():
        """Check system health and send alerts if needed"""
        health_status = HealthChecker.get_health_status()
        
        # Check for critical issues
        critical_issues = []
        
        if health_status['database']['status'] == 'unhealthy':
            critical_issues.append('Database connectivity issue')
        
        if health_status['disk_space']['status'] == 'critical':
            critical_issues.append(f"Low disk space: {health_status['disk_space']['free_space_percent']}% free")
        
        if health_status['memory']['status'] == 'critical':
            critical_issues.append(f"High memory usage: {health_status['memory']['used_percent']}%")
        
        if critical_issues:
            AlertManager.send_alert(critical_issues)
    
    @staticmethod
    def send_alert(issues):
        """Send alert notification"""
        # This would integrate with your alerting system
        # For now, just log the alert
        current_app.logger.critical(f"ALERT: Critical issues detected: {', '.join(issues)}")
        
        # In production, you might send emails, Slack messages, etc.
        # Example:
        # send_email_alert(issues)
        # send_slack_alert(issues)