import os

class Config:
    """
    Configuration class for the Flask application.
    
    This class defines key settings such as the secret key for security, the database URI,
    and SQLAlchemy-specific configurations.
    """

    # SecretKey is used for securely signing session cookies and other security-related operations.
    SECRET_KEY = os.environ.get("SECRET_KEY") or "this_should_be_changed"
    
    # SQLAlchemyDatabaseURI sets the connection string for the database.
    # It uses the DATABASE_URL environment variable if provided; otherwise, defaults to a local SQLite database.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    
    # SQLAlchemyTrackModifications disables the tracking of object modifications to reduce overhead.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
