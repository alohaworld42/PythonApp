from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db, login_manager

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('data_integration.dashboard'))
        flash('Invalid credentials, please try again.')
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
        return redirect(url_for('data_integration.dashboard'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
