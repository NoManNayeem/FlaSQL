from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
import os

# Initialize the database
db = SQLAlchemy()

# Initialize the LoginManager
login_manager = LoginManager()

# Initialize Bcrypt for password hashing
bcrypt = Bcrypt()

# Function to create and configure the Flask app
def create_app() -> Flask:
    app = Flask(__name__)

    # Configure the app from environment variables or use defaults
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my_top_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///flasql.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize plugins with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf = CSRFProtect(app)
    migrate = Migrate(app, db)

    # Setup the login view for login_required
    login_manager.login_view = 'main.login'

    # Import and register Blueprints
    from .routes import main as main_routes  # Ensure this import is within the function to avoid circular imports
    app.register_blueprint(main_routes)

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str):
        from .models import User  # Local import to avoid circular dependencies
        return User.query.get(int(user_id))

    return app

