from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.routes.auth import auth as auth_blueprint
    from app.routes.data_integration import data_integration as data_integration_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(data_integration_blueprint)

    return app

from app import models
