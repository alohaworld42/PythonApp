from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """User dashboard route."""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@main_bp.route('/about')
def about():
    """About page route."""
    return render_template('about.html')