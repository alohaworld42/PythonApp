"""
Performance monitoring utilities for tracking application performance.
"""

import time
import psutil
import threading
from functools import wraps
from flask import request, g, current_app
from datetime import datetime, timedelta
import json
import os

class PerformanceMonitor:
    """Monitor application performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'requests': [],
            'database_queries': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'system_metrics': []
        }
        self.monitoring_active = True
        self._lock = threading.Lock()
    
    def record_request(self, endpoint, method, response_time, status_code, user_id=None):
        """Record request performance metrics."""
        if not self.monitoring_active:
            return
        
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'method': method,
                'response_time': response_time,
                'status_code': status_code,
                'user_id': user_id
            }
            
            self.metrics['requests'].append(metric)
            
            # Keep only last 1000 requests to prevent memory issues
            if len(self.metrics['requests']) > 1000:
                self.metrics['requests'] = self.metrics['requests'][-1000:]
    
    def record_database_query(self, query_type, execution_time, table=None):
        """Record database query performance."""
        if not self.monitoring_active:
            return
        
        with self._lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'query_type': query_type,
                'execution_time': execution_time,
                'table': table
            }
            
            self.metrics['database_queries'].append(metric)
            
            # Keep only last 500 queries
            if len(self.metrics['database_queries']) > 500:
                self.metrics['database_queries'] = self.metrics['database_queries'][-500:]
    
    def record_cache_hit(self):
        """Record cache hit."""
        with self._lock:
            self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        with self._lock:
            self.metrics['cache_misses'] += 1
    
    def record_system_metrics(self):
        """Record system performance metrics."""
        if not self.monitoring_active:
            return
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metric = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free
            }
            
            with self._lock:
                self.metrics['system_metrics'].append(metric)
                
                # Keep only last 100 system metrics
                if len(self.metrics['system_metrics']) > 100:
                    self.metrics['system_metrics'] = self.metrics['system_metrics'][-100:]
        
        except Exception as e:
            current_app.logger.error(f"Error recording system metrics: {str(e)}")
    
    def get_performance_summary(self, minutes=60):
        """Get performance summary for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            # Filter recent requests
            recent_requests = [
                r for r in self.metrics['requests']
                if datetime.fromisoformat(r['timestamp']) > cutoff_time
            ]
            
            # Filter recent queries
            recent_queries = [
                q for q in self.metrics['database_queries']
                if datetime.fromisoformat(q['timestamp']) > cutoff_time
            ]
            
            # Calculate statistics
            if recent_requests:
                response_times = [r['response_time'] for r in recent_requests]
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Status code distribution
                status_codes = {}
                for req in recent_requests:
                    code = req['status_code']
                    status_codes[code] = status_codes.get(code, 0) + 1
                
                # Endpoint performance
                endpoint_stats = {}
                for req in recent_requests:
                    endpoint = req['endpoint']
                    if endpoint not in endpoint_stats:
                        endpoint_stats[endpoint] = {
                            'count': 0,
                            'total_time': 0,
                            'max_time': 0
                        }
                    
                    endpoint_stats[endpoint]['count'] += 1
                    endpoint_stats[endpoint]['total_time'] += req['response_time']
                    endpoint_stats[endpoint]['max_time'] = max(
                        endpoint_stats[endpoint]['max_time'],
                        req['response_time']
                    )
                
                # Calculate average times
                for endpoint in endpoint_stats:
                    stats = endpoint_stats[endpoint]
                    stats['avg_time'] = stats['total_time'] / stats['count']
            else:
                avg_response_time = 0
                max_response_time = 0
                min_response_time = 0
                status_codes = {}
                endpoint_stats = {}
            
            # Database query statistics
            if recent_queries:
                query_times = [q['execution_time'] for q in recent_queries]
                avg_query_time = sum(query_times) / len(query_times)
                max_query_time = max(query_times)
                
                # Query type distribution
                query_types = {}
                for query in recent_queries:
                    qtype = query['query_type']
                    query_types[qtype] = query_types.get(qtype, 0) + 1
            else:
                avg_query_time = 0
                max_query_time = 0
                query_types = {}
            
            # Cache statistics
            total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
            cache_hit_rate = (
                (self.metrics['cache_hits'] / total_cache_requests * 100)
                if total_cache_requests > 0 else 0
            )
            
            # Latest system metrics
            latest_system = self.metrics['system_metrics'][-1] if self.metrics['system_metrics'] else None
            
            return {
                'time_period_minutes': minutes,
                'request_stats': {
                    'total_requests': len(recent_requests),
                    'avg_response_time': round(avg_response_time, 3),
                    'max_response_time': round(max_response_time, 3),
                    'min_response_time': round(min_response_time, 3),
                    'requests_per_minute': len(recent_requests) / minutes,
                    'status_codes': status_codes,
                    'endpoint_performance': endpoint_stats
                },
                'database_stats': {
                    'total_queries': len(recent_queries),
                    'avg_query_time': round(avg_query_time, 3),
                    'max_query_time': round(max_query_time, 3),
                    'query_types': query_types
                },
                'cache_stats': {
                    'cache_hits': self.metrics['cache_hits'],
                    'cache_misses': self.metrics['cache_misses'],
                    'cache_hit_rate': round(cache_hit_rate, 1)
                },
                'system_stats': latest_system
            }
    
    def get_slow_endpoints(self, threshold=1.0, minutes=60):
        """Get endpoints that are performing slowly."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            recent_requests = [
                r for r in self.metrics['requests']
                if datetime.fromisoformat(r['timestamp']) > cutoff_time
                and r['response_time'] > threshold
            ]
            
            # Group by endpoint
            slow_endpoints = {}
            for req in recent_requests:
                endpoint = req['endpoint']
                if endpoint not in slow_endpoints:
                    slow_endpoints[endpoint] = {
                        'count': 0,
                        'avg_time': 0,
                        'max_time': 0,
                        'times': []
                    }
                
                slow_endpoints[endpoint]['count'] += 1
                slow_endpoints[endpoint]['times'].append(req['response_time'])
                slow_endpoints[endpoint]['max_time'] = max(
                    slow_endpoints[endpoint]['max_time'],
                    req['response_time']
                )
            
            # Calculate averages
            for endpoint in slow_endpoints:
                times = slow_endpoints[endpoint]['times']
                slow_endpoints[endpoint]['avg_time'] = sum(times) / len(times)
                del slow_endpoints[endpoint]['times']  # Remove raw times
            
            # Sort by average time
            sorted_endpoints = sorted(
                slow_endpoints.items(),
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )
            
            return sorted_endpoints
    
    def export_metrics(self, filename=None):
        """Export metrics to JSON file."""
        if filename is None:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with self._lock:
            with open(filename, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        
        return filename
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        with self._lock:
            self.metrics = {
                'requests': [],
                'database_queries': [],
                'cache_hits': 0,
                'cache_misses': 0,
                'system_metrics': []
            }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_request_performance(f):
    """Decorator to monitor request performance."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
        except Exception as e:
            status_code = 500
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            
            # Get user ID if available
            user_id = None
            try:
                from flask_login import current_user
                if hasattr(current_user, 'id'):
                    user_id = current_user.id
            except:
                pass
            
            # Record the request
            performance_monitor.record_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                response_time=response_time,
                status_code=status_code,
                user_id=user_id
            )
        
        return result
    
    return decorated_function

def monitor_database_query(query_type, table=None):
    """Decorator to monitor database query performance."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                
                performance_monitor.record_database_query(
                    query_type=query_type,
                    execution_time=execution_time,
                    table=table
                )
        
        return decorated_function
    return decorator

class SystemMetricsCollector:
    """Background thread to collect system metrics."""
    
    def __init__(self, interval=60):  # Collect every minute
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start collecting system metrics."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collect_metrics)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop collecting system metrics."""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _collect_metrics(self):
        """Background method to collect metrics."""
        while self.running:
            try:
                performance_monitor.record_system_metrics()
                time.sleep(self.interval)
            except Exception as e:
                current_app.logger.error(f"Error in system metrics collection: {str(e)}")
                time.sleep(self.interval)

# Global system metrics collector
system_metrics_collector = SystemMetricsCollector()

def init_performance_monitoring(app):
    """Initialize performance monitoring for the Flask app."""
    
    # Start system metrics collection in production
    if not app.debug and not app.testing:
        system_metrics_collector.start()
    
    # Add performance monitoring to all requests
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            
            # Get user ID if available
            user_id = None
            try:
                from flask_login import current_user
                if hasattr(current_user, 'id'):
                    user_id = current_user.id
            except:
                pass
            
            # Record the request
            performance_monitor.record_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                response_time=response_time,
                status_code=response.status_code,
                user_id=user_id
            )
        
        return response
    
    # Add performance monitoring endpoints
    @app.route('/admin/performance')
    def performance_dashboard():
        """Admin endpoint to view performance dashboard."""
        if not app.debug:
            from flask import abort
            abort(404)  # Only available in debug mode
        
        from flask import render_template
        return render_template('admin/performance_dashboard.html')
    
    @app.route('/api/performance/summary')
    def performance_api():
        """API endpoint for performance data."""
        if not app.debug:
            from flask import abort
            abort(404)  # Only available in debug mode
        
        from flask import request, jsonify
        minutes = request.args.get('minutes', 60, type=int)
        
        summary = performance_monitor.get_performance_summary(minutes)
        slow_endpoints = performance_monitor.get_slow_endpoints(minutes=minutes)
        recommendations = get_performance_recommendations()
        
        return jsonify({
            **summary,
            'slow_endpoints': slow_endpoints,
            'recommendations': recommendations
        })

def get_performance_recommendations():
    """Get performance optimization recommendations based on collected metrics."""
    summary = performance_monitor.get_performance_summary()
    recommendations = []
    
    # Check response times
    if summary['request_stats']['avg_response_time'] > 1.0:
        recommendations.append({
            'type': 'response_time',
            'severity': 'high',
            'message': f"Average response time is {summary['request_stats']['avg_response_time']:.3f}s",
            'suggestion': 'Consider implementing caching or optimizing database queries'
        })
    
    # Check database performance
    if summary['database_stats']['avg_query_time'] > 0.5:
        recommendations.append({
            'type': 'database',
            'severity': 'medium',
            'message': f"Average database query time is {summary['database_stats']['avg_query_time']:.3f}s",
            'suggestion': 'Add database indexes or optimize slow queries'
        })
    
    # Check cache hit rate
    if summary['cache_stats']['cache_hit_rate'] < 70:
        recommendations.append({
            'type': 'cache',
            'severity': 'medium',
            'message': f"Cache hit rate is only {summary['cache_stats']['cache_hit_rate']:.1f}%",
            'suggestion': 'Review caching strategy and increase cache TTL for stable data'
        })
    
    # Check system resources
    if summary['system_stats']:
        if summary['system_stats']['cpu_percent'] > 80:
            recommendations.append({
                'type': 'system',
                'severity': 'high',
                'message': f"CPU usage is {summary['system_stats']['cpu_percent']:.1f}%",
                'suggestion': 'Consider scaling up server resources or optimizing CPU-intensive operations'
            })
        
        if summary['system_stats']['memory_percent'] > 85:
            recommendations.append({
                'type': 'system',
                'severity': 'high',
                'message': f"Memory usage is {summary['system_stats']['memory_percent']:.1f}%",
                'suggestion': 'Investigate memory leaks or increase server memory'
            })
    
    return recommendations