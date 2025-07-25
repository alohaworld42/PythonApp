from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, html_body, text_body=None):
    """Send an email."""
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    if text_body:
        msg.body = text_body
    
    # Send email asynchronously
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def send_password_reset_email(user):
    """Send password reset email to user."""
    token = user.get_reset_token()
    reset_url = f"{current_app.config['SITE_URL']}/auth/reset_password/{token}"
    
    subject = "BuyRoll - Password Reset Request"
    recipients = [user.email]
    
    html_body = render_template(
        'email/reset_password.html',
        user=user,
        reset_url=reset_url
    )
    
    text_body = render_template(
        'email/reset_password.txt',
        user=user,
        reset_url=reset_url
    )
    
    send_email(subject, recipients, html_body, text_body)

def send_email_verification(user):
    """Send email verification to user."""
    token = user.generate_email_verification_token()
    verification_url = f"{current_app.config['SITE_URL']}/auth/verify_email/{token}"
    
    subject = "BuyRoll - Verify Your Email"
    recipients = [user.email]
    
    html_body = render_template(
        'email/verify_email.html',
        user=user,
        verification_url=verification_url
    )
    
    text_body = render_template(
        'email/verify_email.txt',
        user=user,
        verification_url=verification_url
    )
    
    send_email(subject, recipients, html_body, text_body)