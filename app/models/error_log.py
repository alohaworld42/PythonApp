"""
Error logging models for tracking application errors
"""
from datetime import datetime
from app import db

class ErrorLog(db.Model):
    """Model for storing application error logs"""
    
    __tablename__ = 'error_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default='medium')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    context = db.Column(db.Text)  # JSON string
    request_data = db.Column(db.Text)  # JSON string
    traceback = db.Column(db.Text)
    environment = db.Column(db.String(50))
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolution_notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='error_logs')
    resolver = db.relationship('User', foreign_keys=[resolved_by])
    feedback = db.relationship('ErrorFeedback', backref='error_log', lazy='dynamic')
    
    def __repr__(self):
        return f'<ErrorLog {self.id}: {self.error_type}>'
    
    def to_dict(self):
        """Convert error log to dictionary"""
        import json
        
        return {
            'id': self.id,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'severity': self.severity,
            'user_id': self.user_id,
            'context': json.loads(self.context) if self.context else None,
            'request_data': json.loads(self.request_data) if self.request_data else None,
            'environment': self.environment,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'resolution_notes': self.resolution_notes,
            'timestamp': self.timestamp.isoformat(),
            'feedback_count': self.feedback.count()
        }
    
    def mark_resolved(self, resolver_id, notes=None):
        """Mark error as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()
        self.resolved_by = resolver_id
        self.resolution_notes = notes
        db.session.commit()
    
    @classmethod
    def get_unresolved_errors(cls, severity=None, limit=50):
        """Get unresolved errors, optionally filtered by severity"""
        query = cls.query.filter_by(resolved=False)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_error_stats(cls, days=30):
        """Get error statistics for the last N days"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_errors = cls.query.filter(cls.timestamp >= cutoff_date).count()
        resolved_errors = cls.query.filter(
            cls.timestamp >= cutoff_date,
            cls.resolved == True
        ).count()
        
        severity_counts = db.session.query(
            cls.severity,
            db.func.count(cls.id)
        ).filter(cls.timestamp >= cutoff_date).group_by(cls.severity).all()
        
        error_type_counts = db.session.query(
            cls.error_type,
            db.func.count(cls.id)
        ).filter(cls.timestamp >= cutoff_date).group_by(cls.error_type).order_by(
            db.func.count(cls.id).desc()
        ).limit(10).all()
        
        return {
            'total_errors': total_errors,
            'resolved_errors': resolved_errors,
            'resolution_rate': (resolved_errors / total_errors * 100) if total_errors > 0 else 0,
            'severity_breakdown': dict(severity_counts),
            'top_error_types': dict(error_type_counts)
        }

class ErrorFeedback(db.Model):
    """Model for storing user feedback about errors"""
    
    __tablename__ = 'error_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    error_id = db.Column(db.Integer, db.ForeignKey('error_logs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedback_type = db.Column(db.String(50), default='general')  # general, bug_report, feature_request
    message = db.Column(db.Text)
    steps_to_reproduce = db.Column(db.Text)
    expected_behavior = db.Column(db.Text)
    actual_behavior = db.Column(db.Text)
    browser_info = db.Column(db.String(200))
    additional_info = db.Column(db.Text)  # JSON string
    helpful = db.Column(db.Boolean)  # Was this feedback helpful?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='error_feedback')
    
    def __repr__(self):
        return f'<ErrorFeedback {self.id}: {self.feedback_type}>'
    
    def to_dict(self):
        """Convert feedback to dictionary"""
        import json
        
        return {
            'id': self.id,
            'error_id': self.error_id,
            'user_id': self.user_id,
            'feedback_type': self.feedback_type,
            'message': self.message,
            'steps_to_reproduce': self.steps_to_reproduce,
            'expected_behavior': self.expected_behavior,
            'actual_behavior': self.actual_behavior,
            'browser_info': self.browser_info,
            'additional_info': json.loads(self.additional_info) if self.additional_info else None,
            'helpful': self.helpful,
            'created_at': self.created_at.isoformat(),
            'user_name': self.user.name if self.user else None
        }

class ErrorPattern(db.Model):
    """Model for tracking error patterns and trends"""
    
    __tablename__ = 'error_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(100), nullable=False)
    error_type = db.Column(db.String(100), nullable=False)
    pattern_regex = db.Column(db.String(500))  # Regex to match error messages
    description = db.Column(db.Text)
    solution = db.Column(db.Text)
    occurrence_count = db.Column(db.Integer, default=0)
    last_occurrence = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ErrorPattern {self.id}: {self.pattern_name}>'
    
    def increment_occurrence(self):
        """Increment the occurrence count"""
        self.occurrence_count += 1
        self.last_occurrence = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'pattern_name': self.pattern_name,
            'error_type': self.error_type,
            'description': self.description,
            'solution': self.solution,
            'occurrence_count': self.occurrence_count,
            'last_occurrence': self.last_occurrence.isoformat() if self.last_occurrence else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }