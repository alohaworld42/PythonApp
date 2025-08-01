from flask import Blueprint, render_template
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Sample items data - replace with actual data from your database
    items = [
        {
            'title': 'Wireless Headphones',
            'description': 'Premium noise-cancelling headphones',
            'image': 'https://via.placeholder.com/300x200/55970f/ffffff?text=Headphones',
            'url': 'https://example.com/headphones'
        },
        {
            'title': 'Smart Watch',
            'description': 'Feature-rich smartwatch with health tracking',
            'image': 'https://via.placeholder.com/300x200/6abe11/ffffff?text=Smart+Watch',
            'url': 'https://example.com/smartwatch'
        },
        {
            'title': 'Coffee Maker',
            'description': 'Programmable coffee maker with WiFi',
            'image': 'https://via.placeholder.com/300x200/8DC63F/ffffff?text=Coffee+Maker',
            'url': 'https://example.com/coffee'
        }
    ]
    return render_template('index_clean.html', items=items, title='Home')

@main.route('/products')
def products():
    return render_template('products_clean.html', title='Products')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@main.route('/submit_item')
def submit_item():
    return render_template('submit_item.html', title='Submit Item')

@main.route('/submit_url')
def submit_url():
    return render_template('submit_url.html', title='Submit URL')
