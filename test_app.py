#!/usr/bin/env python3
"""
Simple test Flask app to demonstrate the frontend features
without complex dependencies
"""

from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Configure static files
app.static_folder = 'static'
app.template_folder = 'templates'

@app.route('/')
def index():
    """Homepage route"""
    # Sample data for testing
    items = [
        {
            'name': 'Wireless Headphones',
            'description': 'Premium wireless headphones with noise cancellation',
            'image': 'https://via.placeholder.com/300x200',
            'url': '#',
            'title': 'Wireless Headphones'
        },
        {
            'name': 'Smart Watch',
            'description': 'Advanced smartwatch with health monitoring',
            'image': 'https://via.placeholder.com/300x200',
            'url': '#',
            'title': 'Smart Watch'
        },
        {
            'name': 'Laptop Stand',
            'description': 'Ergonomic laptop stand for better posture',
            'image': 'https://via.placeholder.com/300x200',
            'url': '#',
            'title': 'Laptop Stand'
        }
    ]
    return render_template('index.html', items=items)

@app.route('/dashboard')
def dashboard():
    """Dashboard route"""
    return render_template('dashboard.html')

@app.route('/products')
def products():
    """Products route"""
    return render_template('products.html')

@app.route('/submit_item')
def submit_item():
    """Submit item route"""
    return render_template('submit_item.html')

@app.route('/submit_url')
def submit_url():
    """Submit URL route"""
    return render_template('submit_url.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest"""
    return send_from_directory(app.static_folder, 'manifest.json')

@app.route('/sw.js')
def service_worker():
    """Serve service worker"""
    return send_from_directory(os.path.join(app.static_folder, 'js'), 'sw.js')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("🚀 Starting BuyRoll Test Server...")
    print("📱 Features available:")
    print("   • Dark/Light mode toggle")
    print("   • Advanced search with voice commands")
    print("   • PWA installation")
    print("   • Interactive dashboard")
    print("   • Advanced product showcase")
    print("   • Responsive design")
    print("   • Accessibility features")
    print("\n🌐 Open your browser and visit:")
    print("   • Homepage: http://localhost:5000")
    print("   • Dashboard: http://localhost:5000/dashboard")
    print("   • Products: http://localhost:5000/products")
    print("\n💡 Try these features:")
    print("   • Toggle dark mode in navigation")
    print("   • Use voice search (click microphone)")
    print("   • Install as PWA on mobile")
    print("   • Test responsive design")
    
    app.run(debug=True, host='0.0.0.0', port=5000)