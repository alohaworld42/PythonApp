from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models.user import User

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        """Validate that email is not already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one or log in.')

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    """Form for updating user profile."""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profile_image = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Profile')
    
    def validate_email(self, email):
        """Validate that new email is not already taken by another user."""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already taken. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    """Form for changing password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class PrivacySettingsForm(FlaskForm):
    """Form for privacy settings."""
    profile_visibility = BooleanField('Public Profile')
    show_email = BooleanField('Show Email')
    default_sharing = BooleanField('Share New Purchases by Default')
    show_price = BooleanField('Show Prices')
    friend_requests = SelectField('Who Can Send Friend Requests', choices=[
        ('everyone', 'Everyone'),
        ('friends_of_friends', 'Friends of Friends'),
        ('nobody', 'Nobody')
    ])
    analytics_consent = BooleanField('Analytics Consent')
    personalized_recommendations = BooleanField('Personalized Recommendations')
    submit = SubmitField('Save Settings')

class NotificationSettingsForm(FlaskForm):
    """Form for notification settings."""
    email_friend_requests = BooleanField('Email Friend Requests')
    email_comments = BooleanField('Email Comments')
    email_likes = BooleanField('Email Likes')
    email_new_friend_purchases = BooleanField('Email New Friend Purchases')
    email_system_updates = BooleanField('Email System Updates')
    
    app_friend_requests = BooleanField('App Friend Requests')
    app_comments = BooleanField('App Comments')
    app_likes = BooleanField('App Likes')
    app_new_friend_purchases = BooleanField('App New Friend Purchases')
    app_system_updates = BooleanField('App System Updates')
    
    notification_frequency = SelectField('Email Digest Frequency', choices=[
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest')
    ])
    
    submit = SubmitField('Save Settings')

class RequestResetForm(FlaskForm):
    """Form for requesting password reset."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
    
    def validate_email(self, email):
        """Validate that email exists in the database."""
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    """Form for resetting password."""
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class DashboardSettingsForm(FlaskForm):
    """Form for dashboard customization settings."""
    default_view = SelectField('Default View', choices=[
        ('grid', 'Grid View'),
        ('list', 'List View')
    ])
    
    items_per_page = SelectField('Items Per Page', choices=[
        ('12', '12 items'),
        ('24', '24 items'),
        ('36', '36 items'),
        ('48', '48 items')
    ])
    
    default_sort = SelectField('Default Sort Order', choices=[
        ('date-desc', 'Newest First'),
        ('date-asc', 'Oldest First'),
        ('price-desc', 'Price: High to Low'),
        ('price-asc', 'Price: Low to High'),
        ('store', 'Store Name')
    ])
    
    # Widget visibility settings
    show_quick_stats = BooleanField('Show Quick Stats', default=True)
    show_friend_activity = BooleanField('Show Friend Activity', default=True)
    show_recent_purchases = BooleanField('Show Recent Purchases', default=True)
    show_spending_chart = BooleanField('Show Spending Chart', default=False)
    
    # Widget order settings
    widget_order = StringField('Widget Order (JSON)', default='["quick_stats", "recent_purchases", "friend_activity"]')
    
    # Layout settings
    sidebar_collapsed = BooleanField('Collapse Sidebar by Default', default=False)
    compact_mode = BooleanField('Compact Mode', default=False)
    
    submit = SubmitField('Save Dashboard Settings')