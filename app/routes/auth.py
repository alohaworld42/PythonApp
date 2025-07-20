from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models.user import User
from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestResetForm
from app.utils.oauth import OAuthSignIn, process_oauth_login
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=hashed_password,
            profile_image='default.jpg'
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/logout')
def logout():
    """User logout route."""
    logout_user()
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
            # Send reset email
            # This would be implemented with actual email sending
            pass
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password_hash = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_token.html', title='Reset Password', form=form)

@auth_bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    """Authorize with OAuth provider."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    oauth = OAuthSignIn.get_provider(provider)
    if not oauth:
        flash(f"Unknown provider: {provider}", 'danger')
        return redirect(url_for('auth.login'))
    
    return redirect(oauth.authorize())

@auth_bp.route('/callback/<provider>')
def oauth_callback(provider):
    """Handle OAuth callback."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    oauth = OAuthSignIn.get_provider(provider)
    if not oauth:
        flash(f"Unknown provider: {provider}", 'danger')
        return redirect(url_for('auth.login'))
    
    email, name, profile_image = oauth.callback()
    
    if email is None:
        flash('Authentication failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Process the OAuth login
    user = process_oauth_login(email, name, profile_image)
    
    # Log in the user
    login_user(user, remember=True)
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    flash(f'Successfully logged in with {provider.capitalize()}!', 'success')
    return redirect(url_for('main.dashboard'))