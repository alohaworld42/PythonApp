from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
import hmac
from app import db, bcrypt
from app.models.user import User
from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestResetForm
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Set session duration based on remember me option
            if form.remember.data:
                # Set session to permanent and configure lifetime
                session.permanent = True
                current_app.permanent_session_lifetime = timedelta(days=30)
            else:
                # Default session lifetime (usually until browser closes)
                session.permanent = False
            
            login_user(user, remember=form.remember.data)
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Generate CSRF token for the session if not already present
            if '_csrf_token' not in session:
                session['_csrf_token'] = secrets.token_hex(16)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            # Use consistent error message to prevent user enumeration
            flash('Invalid email or password. Please try again.', 'danger')
            # Add a small delay to prevent timing attacks
            import time
            time.sleep(0.5)
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password with bcrypt
        hashed_password = User.hash_password(form.password.data)
        
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=hashed_password,
            profile_image='default.jpg',
            is_email_verified=False
        )
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        # Auto-verify the account (email verification disabled for now)
        user.is_email_verified = True
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
def logout():
    """User logout route."""
    logout_user()
    # Clear session data
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """Password reset request route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Password reset email functionality disabled for now
            pass
        
        # Always show the same message to prevent user enumeration
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Password reset with token route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Hash the new password
        hashed_password = User.hash_password(form.password.data)
        user.password_hash = hashed_password
        db.session.commit()
        
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_token.html', title='Reset Password', form=form)

def is_safe_url(target):
    """Check if URL is safe for redirection."""
    ref_url = request.host_url
    test_url = target
    # Make sure the URL is relative or points to the same site
    return test_url.startswith('/') or test_url.startswith(ref_url)

# CSRF Protection
@auth_bp.before_request
def csrf_protect():
    """Protect against CSRF attacks."""
    if request.method == "POST":
        token = session.get('_csrf_token')
        form_token = request.form.get('_csrf_token')
        
        if not token or not form_token or not hmac.compare_digest(token, form_token):
            flash('The form has expired. Please try again.', 'danger')
            return redirect(url_for('main.index'))