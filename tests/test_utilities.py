"""
Unit tests for utility functions.
"""
import pytest
from datetime import datetime, timedelta
from app.utils.forms import LoginForm, RegistrationForm, ResetPasswordForm
from app.services.analytics_service import AnalyticsService
from app.services.purchase_sharing_service import PurchaseSharingService
from app.services.notification_service import NotificationService

class TestForms:
    """Test cases for form utilities."""
    
    def test_login_form_validation(self, app):
        """Test login form validation."""
        with app.app_context():
            # Valid form
            form = LoginForm(data={
                'email': 'test@example.com',
                'password': 'testpassword'
            })
            assert form.validate() is True
            
            # Invalid email
            form = LoginForm(data={
                'email': 'invalid-email',
                'password': 'testpassword'
            })
            assert form.validate() is False
            assert 'Invalid email address' in str(form.email.errors)
            
            # Missing password
            form = LoginForm(data={
                'email': 'test@example.com',
                'password': ''
            })
            assert form.validate() is False
            assert 'This field is required' in str(form.password.errors)
    
    def test_registration_form_validation(self, app):
        """Test registration form validation."""
        with app.app_context():
            # Valid form
            form = RegistrationForm(data={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'testpassword123',
                'confirm_password': 'testpassword123'
            })
            assert form.validate() is True
            
            # Password mismatch
            form = RegistrationForm(data={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'testpassword123',
                'confirm_password': 'differentpassword'
            })
            assert form.validate() is False
            
            # Short password
            form = RegistrationForm(data={
                'name': 'Test User',
                'email': 'test@example.com',
                'password': '123',
                'confirm_password': '123'
            })
            assert form.validate() is False
            
            # Missing name
            form = RegistrationForm(data={
                'name': '',
                'email': 'test@example.com',
                'password': 'testpassword123',
                'confirm_password': 'testpassword123'
            })
            assert form.validate() is False
    
    def test_reset_password_form_validation(self, app):
        """Test reset password form validation."""
        with app.app_context():
            # Valid form
            form = ResetPasswordForm(data={
                'password': 'newpassword123',
                'confirm_password': 'newpassword123'
            })
            assert form.validate() is True
            
            # Password mismatch
            form = ResetPasswordForm(data={
                'password': 'newpassword123',
                'confirm_password': 'differentpassword'
            })
            assert form.validate() is False

class TestAnalyticsService:
    """Test cases for analytics service utilities."""
    
    def test_calculate_percentage(self, app):
        """Test percentage calculation utility."""
        with app.app_context():
            # Test normal calculation
            result = AnalyticsService._calculate_percentage(25, 100)
            assert result == 25.0
            
            # Test zero total
            result = AnalyticsService._calculate_percentage(25, 0)
            assert result == 0.0
            
            # Test zero value
            result = AnalyticsService._calculate_percentage(0, 100)
            assert result == 0.0
    
    def test_format_currency(self, app):
        """Test currency formatting utility."""
        with app.app_context():
            # Test USD formatting
            result = AnalyticsService._format_currency(123.45, 'USD')
            assert '$123.45' in result
            
            # Test EUR formatting
            result = AnalyticsService._format_currency(123.45, 'EUR')
            assert '123.45' in result
            
            # Test large numbers
            result = AnalyticsService._format_currency(1234567.89, 'USD')
            assert '1,234,567.89' in result or '1234567.89' in result
    
    def test_date_range_validation(self, app):
        """Test date range validation utility."""
        with app.app_context():
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Valid date range
            is_valid = AnalyticsService._validate_date_range(start_date, end_date)
            assert is_valid is True
            
            # Invalid date range (start after end)
            is_valid = AnalyticsService._validate_date_range(end_date, start_date)
            assert is_valid is False
    
    def test_month_name_conversion(self, app):
        """Test month number to name conversion."""
        with app.app_context():
            month_name = AnalyticsService._get_month_name(1)
            assert month_name == 'January'
            
            month_name = AnalyticsService._get_month_name(12)
            assert month_name == 'December'
            
            # Test invalid month
            month_name = AnalyticsService._get_month_name(13)
            assert month_name == 'Unknown'

class TestPurchaseSharingService:
    """Test cases for purchase sharing service utilities."""
    
    def test_validate_share_comment(self, app):
        """Test share comment validation."""
        with app.app_context():
            # Valid comment
            is_valid = PurchaseSharingService._validate_share_comment('Great product!')
            assert is_valid is True
            
            # Empty comment (should be valid)
            is_valid = PurchaseSharingService._validate_share_comment('')
            assert is_valid is True
            
            # None comment (should be valid)
            is_valid = PurchaseSharingService._validate_share_comment(None)
            assert is_valid is True
            
            # Too long comment
            long_comment = 'x' * 1001  # Assuming 1000 char limit
            is_valid = PurchaseSharingService._validate_share_comment(long_comment)
            assert is_valid is False
    
    def test_sanitize_share_comment(self, app):
        """Test share comment sanitization."""
        with app.app_context():
            # Test HTML sanitization
            comment = '<script>alert("xss")</script>Great product!'
            sanitized = PurchaseSharingService._sanitize_share_comment(comment)
            assert '<script>' not in sanitized
            assert 'Great product!' in sanitized
            
            # Test normal text
            comment = 'This is a normal comment.'
            sanitized = PurchaseSharingService._sanitize_share_comment(comment)
            assert sanitized == comment
    
    def test_generate_feed_item(self, app, test_user, test_purchases):
        """Test feed item generation."""
        with app.app_context():
            purchase = test_purchases[0]
            feed_item = PurchaseSharingService._generate_feed_item(purchase)
            
            assert 'purchase' in feed_item
            assert 'user' in feed_item
            assert 'interactions' in feed_item
            assert feed_item['purchase']['id'] == purchase.id
            assert feed_item['user']['id'] == test_user.id

class TestNotificationService:
    """Test cases for notification service utilities."""
    
    def test_create_notification_data(self, app):
        """Test notification data creation."""
        with app.app_context():
            notification_data = NotificationService._create_notification_data(
                type='friend_request',
                title='New Friend Request',
                message='John Doe sent you a friend request',
                data={'user_id': 123}
            )
            
            assert notification_data['type'] == 'friend_request'
            assert notification_data['title'] == 'New Friend Request'
            assert notification_data['message'] == 'John Doe sent you a friend request'
            assert notification_data['data']['user_id'] == 123
            assert 'timestamp' in notification_data
    
    def test_validate_notification_type(self, app):
        """Test notification type validation."""
        with app.app_context():
            # Valid types
            valid_types = ['friend_request', 'like', 'comment', 'purchase_shared']
            for notification_type in valid_types:
                is_valid = NotificationService._validate_notification_type(notification_type)
                assert is_valid is True
            
            # Invalid type
            is_valid = NotificationService._validate_notification_type('invalid_type')
            assert is_valid is False
    
    def test_format_notification_message(self, app):
        """Test notification message formatting."""
        with app.app_context():
            # Friend request message
            message = NotificationService._format_notification_message(
                'friend_request',
                {'user_name': 'John Doe'}
            )
            assert 'John Doe' in message
            assert 'friend request' in message.lower()
            
            # Like message
            message = NotificationService._format_notification_message(
                'like',
                {'user_name': 'Jane Smith', 'product_name': 'iPhone'}
            )
            assert 'Jane Smith' in message
            assert 'iPhone' in message

class TestEmailUtilities:
    """Test cases for email utility functions."""
    
    def test_email_validation(self, app):
        """Test email validation utility."""
        with app.app_context():
            from app.utils.email import validate_email
            
            # Valid emails
            valid_emails = [
                'test@example.com',
                'user.name@domain.co.uk',
                'user+tag@example.org'
            ]
            
            for email in valid_emails:
                assert validate_email(email) is True
            
            # Invalid emails
            invalid_emails = [
                'invalid-email',
                '@example.com',
                'user@',
                'user@.com'
            ]
            
            for email in invalid_emails:
                assert validate_email(email) is False
    
    def test_email_domain_extraction(self, app):
        """Test email domain extraction."""
        with app.app_context():
            from app.utils.email import extract_domain
            
            domain = extract_domain('user@example.com')
            assert domain == 'example.com'
            
            domain = extract_domain('test.user@subdomain.example.org')
            assert domain == 'subdomain.example.org'
            
            # Invalid email
            domain = extract_domain('invalid-email')
            assert domain is None

class TestSecurityUtilities:
    """Test cases for security utility functions."""
    
    def test_generate_secure_token(self, app):
        """Test secure token generation."""
        with app.app_context():
            from app.utils.security import generate_secure_token
            
            token1 = generate_secure_token()
            token2 = generate_secure_token()
            
            # Tokens should be different
            assert token1 != token2
            
            # Tokens should be strings
            assert isinstance(token1, str)
            assert isinstance(token2, str)
            
            # Tokens should have reasonable length
            assert len(token1) >= 16
            assert len(token2) >= 16
    
    def test_hash_verification(self, app):
        """Test hash verification utility."""
        with app.app_context():
            from app.utils.security import verify_hash
            
            data = 'test_data'
            hash_value = 'expected_hash'
            
            # This would test actual hash verification
            # Implementation depends on your specific hash function
            pass
    
    def test_sanitize_input(self, app):
        """Test input sanitization."""
        with app.app_context():
            from app.utils.security import sanitize_input
            
            # Test HTML sanitization
            dirty_input = '<script>alert("xss")</script>Hello World'
            clean_input = sanitize_input(dirty_input)
            
            assert '<script>' not in clean_input
            assert 'Hello World' in clean_input
            
            # Test SQL injection prevention
            sql_input = "'; DROP TABLE users; --"
            clean_input = sanitize_input(sql_input)
            
            # Should escape or remove dangerous characters
            assert 'DROP TABLE' not in clean_input or "'" not in clean_input

class TestDateUtilities:
    """Test cases for date utility functions."""
    
    def test_format_relative_time(self, app):
        """Test relative time formatting."""
        with app.app_context():
            from app.utils.date import format_relative_time
            
            now = datetime.now()
            
            # Test recent time
            recent = now - timedelta(minutes=5)
            formatted = format_relative_time(recent)
            assert '5 minutes ago' in formatted or 'minutes ago' in formatted
            
            # Test hours ago
            hours_ago = now - timedelta(hours=2)
            formatted = format_relative_time(hours_ago)
            assert '2 hours ago' in formatted or 'hours ago' in formatted
            
            # Test days ago
            days_ago = now - timedelta(days=3)
            formatted = format_relative_time(days_ago)
            assert '3 days ago' in formatted or 'days ago' in formatted
    
    def test_parse_date_string(self, app):
        """Test date string parsing."""
        with app.app_context():
            from app.utils.date import parse_date_string
            
            # Test ISO format
            date_str = '2023-06-15T10:30:00'
            parsed_date = parse_date_string(date_str)
            assert parsed_date.year == 2023
            assert parsed_date.month == 6
            assert parsed_date.day == 15
            
            # Test invalid format
            invalid_date = 'invalid-date'
            parsed_date = parse_date_string(invalid_date)
            assert parsed_date is None
    
    def test_get_date_range(self, app):
        """Test date range generation."""
        with app.app_context():
            from app.utils.date import get_date_range
            
            end_date = datetime(2023, 6, 15)
            start_date, end_date_result = get_date_range('last_30_days', end_date)
            
            assert end_date_result == end_date
            assert start_date == end_date - timedelta(days=30)
            
            # Test monthly range
            start_date, end_date_result = get_date_range('this_month', end_date)
            assert start_date.day == 1
            assert start_date.month == end_date.month
            assert start_date.year == end_date.year