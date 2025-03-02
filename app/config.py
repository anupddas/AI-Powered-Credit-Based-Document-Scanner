import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "this_should_be_changed"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False