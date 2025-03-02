from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    # Primary key for the User model.
    id = db.Column(db.Integer, primary_key=True)
    
    # Unique username for each user.
    username = db.Column(db.String(64), unique=True, nullable=False)
    
    # Unique email address for each user.
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Securely stored hashed password.
    passwordHash = db.Column(db.String(128), nullable=False)
    
    # Role assigned to the user (e.g., 'user' or 'admin').
    role = db.Column(db.String(20), default='user')
    
    # Count of document scans performed by the user in the current day.
    dailyScanCount = db.Column(db.Integer, default=0)
    
    # The date when the last scan was recorded.
    lastScanDate = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Additional approved scan credits beyond the daily free limit.
    extraCredits = db.Column(db.Integer, default=0)

    def setPassword(self, password):
        """
        Generates and sets a secure hash for the provided plaintext password.
        
        Args:
            password (str): The plaintext password to be hashed.
        """
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        """
        Validates the provided password against the stored password hash.
        
        Args:
            password (str): The plaintext password to verify.
        
        Returns:
            bool: True if the password is correct, otherwise False.
        """
        return check_password_hash(self.passwordHash, password)
    
    def __repr__(self):
        """
        Returns a string representation of the User instance.
        """
        return f"<User {self.username}>"

class CreditRequest(db.Model):
    # Primary key for the CreditRequest model.
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key linking the credit request to a user.
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Date when the credit request was submitted.
    requestDate = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Status of the credit request (e.g., 'pending', 'approved', or 'rejected').
    status = db.Column(db.String(20), default='pending')
    
    # Number of additional scan credits requested.
    requestedCredits = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        """
        Returns a string representation of the CreditRequest instance.
        """
        return f"<CreditRequest User:{self.userId} Credits:{self.requestedCredits} Status:{self.status}>"
