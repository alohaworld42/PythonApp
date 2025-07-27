#!/usr/bin/env python3
"""
Database migration script for BuyRoll application
"""
import os
import sys
import sqlite3
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Product, Purchase, Connection, Interaction, StoreIntegration

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    db.create_all()
    print("✓ Database tables created successfully")

def drop_tables():
    """Drop all database tables"""
    print("Dropping database tables...")
    db.drop_all()
    print("✓ Database tables dropped successfully")

def migrate_to_latest():
    """Run all pending migrations"""
    print("Running database migrations...")
    
    # Check if we need to run any specific migrations
    # This is where you would add version-specific migration logic
    
    # For now, just ensure all tables exist
    create_tables()
    print("✓ Database migration completed")

def seed_data():
    """Seed the database with initial data"""
    print("Seeding database with initial data...")
    
    # Add any initial data here
    # For example, default categories, admin users, etc.
    
    db.session.commit()
    print("✓ Database seeded successfully")

def backup_database(backup_path=None):
    """Create a backup of the current database"""
    if backup_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/buyroll_backup_{timestamp}.db"
    
    # Create backups directory if it doesn't exist
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    
    # Get current database path
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if os.path.exists(db_path):
        # Copy the database file
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to {backup_path}")
    else:
        print("⚠ No database file found to backup")

def restore_database(backup_path):
    """Restore database from backup"""
    if not os.path.exists(backup_path):
        print(f"✗ Backup file not found: {backup_path}")
        return False
    
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Create backup of current database before restore
    if os.path.exists(db_path):
        backup_database(f"{db_path}.pre_restore_backup")
    
    # Restore from backup
    import shutil
    shutil.copy2(backup_path, db_path)
    print(f"✓ Database restored from {backup_path}")
    return True

def check_database_health():
    """Check database health and integrity"""
    print("Checking database health...")
    
    try:
        app = create_app()
        with app.app_context():
            # Check if all tables exist
            tables = ['user', 'product', 'purchase', 'connection', 'interaction', 'store_integration']
            
            for table in tables:
                result = db.session.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not result.fetchone():
                    print(f"✗ Table '{table}' is missing")
                    return False
            
            # Check basic data integrity
            user_count = User.query.count()
            purchase_count = Purchase.query.count()
            
            print(f"✓ Database health check passed")
            print(f"  - Users: {user_count}")
            print(f"  - Purchases: {purchase_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ Database health check failed: {str(e)}")
        return False

def main():
    """Main migration script"""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command>")
        print("Commands:")
        print("  create    - Create all database tables")
        print("  drop      - Drop all database tables")
        print("  migrate   - Run all pending migrations")
        print("  seed      - Seed database with initial data")
        print("  backup    - Create database backup")
        print("  restore   - Restore from backup")
        print("  health    - Check database health")
        return
    
    command = sys.argv[1]
    
    app = create_app()
    with app.app_context():
        if command == 'create':
            create_tables()
        elif command == 'drop':
            drop_tables()
        elif command == 'migrate':
            migrate_to_latest()
        elif command == 'seed':
            seed_data()
        elif command == 'backup':
            backup_path = sys.argv[2] if len(sys.argv) > 2 else None
            backup_database(backup_path)
        elif command == 'restore':
            if len(sys.argv) < 3:
                print("Usage: python migrate.py restore <backup_path>")
                return
            restore_database(sys.argv[2])
        elif command == 'health':
            check_database_health()
        else:
            print(f"Unknown command: {command}")

if __name__ == '__main__':
    main()