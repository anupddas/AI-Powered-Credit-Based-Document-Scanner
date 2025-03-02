from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    daily_scan_count = db.Column(db.Integer, default=0)
    last_scan_date = db.Column(db.Date, default=datetime.utcnow().date())
    extra_credits = db.Column(db.Integer, default=0)  # Additional approved credits

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class CreditRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    request_date = db.Column(db.Date, default=datetime.utcnow().date())
    status = db.Column(db.String(20), default='pending')  # pending, approved, or rejected
    requested_credits = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<CreditRequest User:{self.user_id} Credits:{self.requested_credits} Status:{self.status}>"