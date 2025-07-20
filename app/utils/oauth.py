import os
import json
import requests
from flask import current_app, url_for, redirect, request, session
from oauthlib.oauth2 import WebApplicationClient
from app import db
from app.models.user import User

class OAuthSignIn:
    """Base class for OAuth sign-in providers."""
    
    providers = None
    
    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config[f'{provider_name.upper()}_OAUTH_CREDENTIALS']
        self.client_id = credentials['id']
        self.client_secret = credentials['secret']
        self.client = WebApplicationClient(self.client_id)
    
    def authorize(self):
        """Get the authorization URL for the provider."""
        pass
    
    def callback(self):
        """Handle the callback from the provider."""
        pass
    
    @classmethod
    def get_provider(cls, provider_name):
        """Get the provider instance by name."""
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.provider_name] = provider
        return cls.providers.get(provider_name)


class GoogleSignIn(OAuthSignIn):
    """Google OAuth sign-in provider."""
    
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = 'google'
        self.auth_url = 'https://accounts.google.com/o/oauth2/auth'
        self.token_url = 'https://accounts.google.com/o/oauth2/token'
        self.user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    
    def authorize(self):
        """Get the authorization URL for Google."""
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        return self.client.prepare_request_uri(
            self.auth_url,
            redirect_uri=redirect_uri,
            scope=['openid', 'email', 'profile']
        )
    
    def callback(self):
        """Handle the callback from Google."""
        if 'error' in request.args:
            return None, None, None
        
        # Get authorization code
        code = request.args.get('code')
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        
        # Prepare and send token request
        token_url, headers, body = self.client.prepare_token_request(
            self.token_url,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(self.client_id, self.client_secret)
        )
        
        # Parse token response
        self.client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        uri, headers, body = self.client.add_token(self.user_info_url)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        if userinfo.get('email'):
            email = userinfo['email']
            name = userinfo.get('name', email.split('@')[0])
            profile_image = userinfo.get('picture', None)
            return email, name, profile_image
        
        return None, None, None


class FacebookSignIn(OAuthSignIn):
    """Facebook OAuth sign-in provider."""
    
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = 'facebook'
        self.auth_url = 'https://www.facebook.com/v12.0/dialog/oauth'
        self.token_url = 'https://graph.facebook.com/v12.0/oauth/access_token'
        self.user_info_url = 'https://graph.facebook.com/v12.0/me'
    
    def authorize(self):
        """Get the authorization URL for Facebook."""
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        return self.client.prepare_request_uri(
            self.auth_url,
            redirect_uri=redirect_uri,
            scope=['email', 'public_profile']
        )
    
    def callback(self):
        """Handle the callback from Facebook."""
        if 'error' in request.args:
            return None, None, None
        
        # Get authorization code
        code = request.args.get('code')
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        
        # Prepare and send token request
        token_url, headers, body = self.client.prepare_token_request(
            self.token_url,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(self.client_id, self.client_secret)
        )
        
        # Parse token response
        self.client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        uri, headers, body = self.client.add_token(
            f"{self.user_info_url}?fields=id,name,email,picture.type(large)"
        )
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        if userinfo.get('email'):
            email = userinfo['email']
            name = userinfo.get('name', email.split('@')[0])
            profile_image = userinfo.get('picture', {}).get('data', {}).get('url', None)
            return email, name, profile_image
        
        return None, None, None


class AmazonSignIn(OAuthSignIn):
    """Amazon OAuth sign-in provider."""
    
    def __init__(self):
        super(AmazonSignIn, self).__init__('amazon')
        self.service = 'amazon'
        self.auth_url = 'https://www.amazon.com/ap/oa'
        self.token_url = 'https://api.amazon.com/auth/o2/token'
        self.user_info_url = 'https://api.amazon.com/user/profile'
    
    def authorize(self):
        """Get the authorization URL for Amazon."""
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        return self.client.prepare_request_uri(
            self.auth_url,
            redirect_uri=redirect_uri,
            scope=['profile', 'profile:user_id', 'profile:email_address', 'profile:name']
        )
    
    def callback(self):
        """Handle the callback from Amazon."""
        if 'error' in request.args:
            return None, None, None
        
        # Get authorization code
        code = request.args.get('code')
        redirect_uri = url_for('auth.oauth_callback', provider=self.provider_name, _external=True)
        
        # Prepare and send token request
        token_url, headers, body = self.client.prepare_token_request(
            self.token_url,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(self.client_id, self.client_secret)
        )
        
        # Parse token response
        self.client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Get user info
        uri, headers, body = self.client.add_token(self.user_info_url)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo = userinfo_response.json()
        
        if userinfo.get('email'):
            email = userinfo['email']
            name = userinfo.get('name', email.split('@')[0])
            # Amazon doesn't provide profile image
            profile_image = None
            return email, name, profile_image
        
        return None, None, None


def process_oauth_login(email, name, profile_image):
    """Process OAuth login and return the user."""
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create a new user
        user = User(
            email=email,
            name=name,
            password_hash='',  # OAuth users don't have a password
            profile_image=profile_image or 'default.jpg'
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update existing user info
        if name and name != user.name:
            user.name = name
        if profile_image and profile_image != user.profile_image:
            # Save profile image
            user.profile_image = save_profile_image(profile_image, email)
            db.session.commit()
    
    return user


def save_profile_image(image_url, email):
    """Save profile image from URL and return the filename."""
    if not image_url:
        return 'default.jpg'
    
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Generate a unique filename
            filename = f"{email.split('@')[0]}_{os.urandom(8).hex()}.jpg"
            filepath = os.path.join(current_app.root_path, 'static', 'images', 'profiles', filename)
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filename
    except Exception as e:
        current_app.logger.error(f"Error saving profile image: {e}")
    
    return 'default.jpg'