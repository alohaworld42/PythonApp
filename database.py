import sqlite3
from sqlite3 import Error

def connect_db():
    try:
        conn = sqlite3.connect('url_metadata.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    try:
        with connect_db() as conn:
            if conn is not None:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS metadata (
                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                             url TEXT NOT NULL,
                             title TEXT NOT NULL,
                             description TEXT NOT NULL,
                             image TEXT NOT NULL)''')
                conn.commit()
            else:
                print("Error! Cannot connect to the database.")
    except Error as e:
        print(f"Error initializing database: {e}")