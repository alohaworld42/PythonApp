"""
Admin routes for error management and system monitoring
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.models.error_log import ErrorLog, ErrorFeedback, ErrorPattern
from app.utils.monitoring import HealthChecker, MetricsCollector
from app import db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Check if user is admin (you'll need to add this field to User model)
        if not getattr(current_user, 'is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get system health
    health_status = HealthChecker.get_health_status()
    
    # Get application metrics
    metrics = MetricsCollector.get_all_metrics()
    
    # Get error statistics
    error_stats = ErrorLog.get_error_stats(days=7)
    
    # Get recent unresolved errors
    recent_errors = ErrorLog.get_unresolved_errors(limit=10)
    
    return render_template('admin/dashboard.html',
                         health_status=health_status,
                         metrics=metrics,
                         error_stats=error_stats,
                         recent_errors=recent_errors)

@admin_bp.route('/errors')
@login_required
@admin_required
def error_list():
    """List all errors with filtering options"""
    page = request.args.get('page', 1, type=int)
    severity = request.args.get('severity')
    resolved = request.args.get('resolved')
    error_type = request.args.get('error_type')
    
    query = ErrorLog.query
    
    # Apply filters
    if severity:
        query = query.filter_by(severity=severity)
    
    if resolved is not None:
        query = query.filter_by(resolved=resolved.lower() == 'true')
    
    if error_type:
        query = query.filter(ErrorLog.error_type.contains(error_type))
    
    # Paginate results
    errors = query.order_by(ErrorLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get filter options
    severity_options = db.session.query(ErrorLog.severity).distinct().all()
    error_type_options = db.session.query(ErrorLog.error_type).distinct().limit(20).all()
    
    return render_template('admin/error_list.html',
                         errors=errors,
                         severity_options=[s[0] for s in severity_options],
                         error_type_options=[e[0] for e in error_type_options],
                         current_filters={
                             'severity': severity,
                             'resolved': resolved,
                             'error_type': error_type
                         })

@admin_bp.route('/errors/<int:error_id>')
@login_required
@admin_required
def error_detail(error_id):
    """View detailed error information"""
    error = ErrorLog.query.get_or_404(error_id)
    feedback = ErrorFeedback.query.filter_by(error_id=error_id).all()
    
    return render_template('admin/error_detail.html',
                         error=error,
                         feedback=feedback)

@admin_bp.route('/errors/<int:error_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_error(error_id):
    """Mark an error as resolved"""
    error = ErrorLog.query.get_or_404(error_id)
    resolution_notes = request.form.get('resolution_notes')
    
    error.mark_resolved(current_user.id, resolution_notes)
    
    flash('Error marked as resolved', 'success')
    return redirect(url_for('admin.error_detail', error_id=error_id))

@admin_bp.route('/api/errors/stats')
@login_required
@admin_required
def error_stats_api():
    """API endpoint for error statistics"""
    days = request.args.get('days', 30, type=int)
    stats = ErrorLog.get_error_stats(days=days)
    return jsonify(stats)

@admin_bp.route('/api/health')
@login_required
@admin_required
def health_api():
    """API endpoint for system health"""
    health_status = HealthChecker.get_health_status()
    return jsonify(health_status)

@admin_bp.route('/api/metrics')
@login_required
@admin_required
def metrics_api():
    """API endpoint for application metrics"""
    metrics = MetricsCollector.get_all_metrics()
    return jsonify(metrics)

@admin_bp.route('/patterns')
@login_required
@admin_required
def error_patterns():
    """View error patterns and trends"""
    patterns = ErrorPattern.query.filter_by(is_active=True).order_by(
        ErrorPattern.occurrence_count.desc()
    ).all()
    
    return render_template('admin/error_patterns.html', patterns=patterns)

@admin_bp.route('/patterns/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_error_pattern():
    """Create a new error pattern"""
    if request.method == 'POST':
        pattern = ErrorPattern(
            pattern_name=request.form['pattern_name'],
            error_type=request.form['error_type'],
            pattern_regex=request.form.get('pattern_regex'),
            description=request.form.get('description'),
            solution=request.form.get('solution')
        )
        
        db.session.add(pattern)
        db.session.commit()
        
        flash('Error pattern created successfully', 'success')
        return redirect(url_for('admin.error_patterns'))
    
    return render_template('admin/create_error_pattern.html')

@admin_bp.route('/logs')
@login_required
@admin_required
def view_logs():
    """View application logs"""
    import os
    
    log_file = os.environ.get('LOG_FILE', 'logs/app.log')
    
    try:
        with open(log_file, 'r') as f:
            # Read last 1000 lines
            lines = f.readlines()[-1000:]
            log_content = ''.join(lines)
    except FileNotFoundError:
        log_content = 'Log file not found'
    except Exception as e:
        log_content = f'Error reading log file: {str(e)}'
    
    return render_template('admin/logs.html', log_content=log_content)

@admin_bp.route('/system-info')
@login_required
@admin_required
def system_info():
    """View system information"""
    import sys
    import platform
    import psutil
    from datetime import datetime
    
    system_info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),
        'disk_total': round(psutil.disk_usage('/').total / (1024**3), 2),
        'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time()),
        'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else 'N/A'
    }
    
    return render_template('admin/system_info.html', system_info=system_info)