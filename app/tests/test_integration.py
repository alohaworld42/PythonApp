import unittest
from app import create_app, db
from app.models import User, Product
from flask import url_for

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register_login(self):
        # Test user registration
        response = self.client.post('/register', data={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

        # Test user login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

    def test_fetch_shopify(self):
        self.test_register_login()
        response = self.client.get('/fetch_shopify')
        self.assertEqual(response.status_code, 200)

    def test_fetch_woocommerce(self):
        self.test_register_login()
        response = self.client.get('/fetch_woocommerce')
        self.assertEqual(response.status_code, 200)

    def test_fetch_magento(self):
        self.test_register_login()
        response = self.client.get('/fetch_magento')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
