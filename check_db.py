import sqlite3

def check_db():
    """Check the database tables."""
    # Connect to the database
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables in the database:")
    for table in tables:
        print(f"- {table['name']}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table['name']})")
        columns = cursor.fetchall()
        
        print("  Columns:")
        for column in columns:
            print(f"    - {column['name']} ({column['type']})")
        
        print()
    
    # Close connection
    conn.close()

if __name__ == '__main__':
    check_db()