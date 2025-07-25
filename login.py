from flask import Flask, request, jsonify
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

DATABASE = os.getenv('DATABASE_URL', 'sqlite:///url_metadata.db')

def connect_db():
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)

    try:
        with connect_db() as conn:
            if conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
        return jsonify({"success": "User registered successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        with connect_db() as conn:
            if conn:
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE username = ?", (username,))
                user = c.fetchone()
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    if user and check_password_hash(user[0], password):
        return jsonify({"success": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True)
