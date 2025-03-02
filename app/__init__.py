from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# Initialize the SQLAlchemy instance to be used across the application.
dbInstance = SQLAlchemy()

def createApp():
    """
    Creates and configures the Flask application.
    
    This function initializes the Flask app, configures it using the provided
    Config object, initializes the database, registers the blueprints, and creates
    all necessary database tables.
    
    Returns:
        flaskApp (Flask): The fully configured Flask application instance.
    """
    # Instantiate the Flask application.
    flaskApp = Flask(__name__)
    
    # Configure the app using the settings defined in the Config class.
    flaskApp.config.from_object(Config)
    
    # Initialize the SQLAlchemy database instance with the Flask application.
    dbInstance.init_app(flaskApp)
    
    # Import and register the main blueprint for handling application routes.
    from app.views import main as mainBlueprint
    flaskApp.register_blueprint(mainBlueprint)
    
    # Create database tables within the application context.
    with flaskApp.app_context():
        dbInstance.create_all()
    
    # Return the configured Flask application instance.
    return flaskApp
