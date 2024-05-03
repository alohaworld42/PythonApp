from flask_login import UserMixin

from application import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def __repr__(self):
        return {'id': self.id,
                'email': self.email,
                'password': self.password}
