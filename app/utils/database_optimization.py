"""
Database optimization utilities for improved query performance.
"""

from app import db
from sqlalchemy import text, Index
from flask import current_app
import time
from functools import wraps

class QueryOptimizer:
    """Utility class for database query optimization."""
    
    @staticmethod
    def create_indexes():
        """Create database indexes for frequently queried columns."""
        try:
            # User table indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);"))
            
            # Purchase table indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_user_id ON purchase(user_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_user_date ON purchase(user_id, purchase_date DESC);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_shared ON purchase(is_shared, purchase_date DESC);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_purchase_store ON purchase(store_name);"))
            
            # Product table indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_product_category ON product(category);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_product_price ON product(price);"))
            
            # Connection table indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_connection_user_status ON connection(user_id, status);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_connection_friend_status ON connection(friend_id, status);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_connection_status ON connection(status);"))
            
            # Interaction table indexes
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_interaction_purchase ON interaction(purchase_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_interaction_user ON interaction(user_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_interaction_type ON interaction(type);"))
            
            # Notification table indexes (if exists)
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_notification_user ON notification(user_id);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_notification_read ON notification(is_read);"))
            db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_notification_created ON notification(created_at DESC);"))
            
            db.session.commit()
            current_app.logger.info("Database indexes created successfully")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating database indexes: {str(e)}")
            raise
    
    @staticmethod
    def analyze_query_performance():
        """Analyze query performance and provide recommendations."""
        try:
            # Check for missing indexes on frequently queried columns
            slow_queries = []
            
            # Simulate some common queries and measure performance
            start_time = time.time()
            
            # Test user lookup by email
            db.session.execute(text("SELECT * FROM user WHERE email = 'test@example.com'"))
            email_query_time = time.time() - start_time
            
            if email_query_time > 0.1:  # 100ms threshold
                slow_queries.append({
                    'query': 'User lookup by email',
                    'time': email_query_time,
                    'recommendation': 'Ensure index on user.email exists'
                })
            
            # Test purchase queries
            start_time = time.time()
            db.session.execute(text("""
                SELECT p.*, pr.* FROM purchase p 
                JOIN product pr ON p.product_id = pr.id 
                WHERE p.user_id = 1 
                ORDER BY p.purchase_date DESC 
                LIMIT 20
            """))
            purchase_query_time = time.time() - start_time
            
            if purchase_query_time > 0.2:  # 200ms threshold
                slow_queries.append({
                    'query': 'User purchases with products',
                    'time': purchase_query_time,
                    'recommendation': 'Ensure indexes on purchase.user_id and purchase.purchase_date exist'
                })
            
            return {
                'slow_queries': slow_queries,
                'total_queries_analyzed': 2,
                'recommendations': [
                    'Create composite indexes for frequently used WHERE clauses',
                    'Consider query result caching for expensive analytics queries',
                    'Use EXPLAIN QUERY PLAN to analyze specific slow queries'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing query performance: {str(e)}")
            return {'error': str(e)}

def query_timer(func):
    """Decorator to time database queries for performance monitoring."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        query_time = end_time - start_time
        if query_time > 0.5:  # Log queries taking more than 500ms
            current_app.logger.warning(
                f"Slow query detected in {func.__name__}: {query_time:.3f}s"
            )
        
        return result
    return wrapper

class DatabaseConnectionPool:
    """Manage database connection pooling for better performance."""
    
    @staticmethod
    def configure_pool(app):
        """Configure database connection pool settings."""
        # SQLite doesn't support connection pooling in the traditional sense
        # But we can configure some performance settings
        
        if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
            # SQLite-specific optimizations
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': 20
                }
            }
        else:
            # PostgreSQL/MySQL connection pool settings
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
                'pool_size': 10,
                'pool_recycle': 3600,
                'pool_pre_ping': True,
                'max_overflow': 20
            }

def optimize_sqlite_settings():
    """Apply SQLite-specific performance optimizations."""
    try:
        # Enable WAL mode for better concurrent access
        db.session.execute(text("PRAGMA journal_mode=WAL;"))
        
        # Increase cache size (in KB)
        db.session.execute(text("PRAGMA cache_size=10000;"))
        
        # Enable foreign key constraints
        db.session.execute(text("PRAGMA foreign_keys=ON;"))
        
        # Optimize synchronous mode for better performance
        db.session.execute(text("PRAGMA synchronous=NORMAL;"))
        
        # Set temp store to memory
        db.session.execute(text("PRAGMA temp_store=MEMORY;"))
        
        # Optimize page size for better performance
        db.session.execute(text("PRAGMA page_size=4096;"))
        
        # Enable memory-mapped I/O
        db.session.execute(text("PRAGMA mmap_size=268435456;"))  # 256MB
        
        # Optimize locking mode
        db.session.execute(text("PRAGMA locking_mode=NORMAL;"))
        
        db.session.commit()
        current_app.logger.info("SQLite performance optimizations applied")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error applying SQLite optimizations: {str(e)}")

def get_query_execution_plan(query):
    """Get query execution plan for optimization analysis."""
    try:
        # Use EXPLAIN QUERY PLAN to analyze query performance
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        result = db.session.execute(text(explain_query)).fetchall()
        
        plan_info = []
        for row in result:
            plan_info.append({
                'id': row[0] if len(row) > 0 else None,
                'parent': row[1] if len(row) > 1 else None,
                'notused': row[2] if len(row) > 2 else None,
                'detail': row[3] if len(row) > 3 else None
            })
        
        return plan_info
        
    except Exception as e:
        current_app.logger.error(f"Error getting query execution plan: {str(e)}")
        return []

def analyze_table_statistics():
    """Analyze table statistics for optimization insights."""
    try:
        stats = {}
        
        # Get table information
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        tables = db.session.execute(text(tables_query)).fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get row count
            count_result = db.session.execute(text(f"SELECT COUNT(*) FROM {table_name}")).fetchone()
            row_count = count_result[0] if count_result else 0
            
            # Get table info
            pragma_result = db.session.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            columns = len(pragma_result)
            
            # Get index information
            index_result = db.session.execute(text(f"PRAGMA index_list({table_name})")).fetchall()
            indexes = len(index_result)
            
            stats[table_name] = {
                'row_count': row_count,
                'column_count': columns,
                'index_count': indexes,
                'estimated_size_kb': row_count * columns * 50 / 1024  # Rough estimate
            }
        
        return stats
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing table statistics: {str(e)}")
        return {}

def vacuum_database():
    """Perform database maintenance to optimize storage and performance."""
    try:
        if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
            # SQLite VACUUM command
            db.session.execute(text("VACUUM;"))
            current_app.logger.info("Database VACUUM completed")
        else:
            # For PostgreSQL, you might want to run ANALYZE
            db.session.execute(text("ANALYZE;"))
            current_app.logger.info("Database ANALYZE completed")
            
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during database maintenance: {str(e)}")