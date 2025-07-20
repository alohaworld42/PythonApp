import sqlite3
import os

def init_db():
    """Initialize the database with schema.sql."""
    # Connect to the database
    conn = sqlite3.connect('app.db')
    
    # Read schema.sql
    with open('schema.sql', 'r') as f:
        schema = f.read()
    
    # Execute schema.sql
    conn.executescript(schema)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()