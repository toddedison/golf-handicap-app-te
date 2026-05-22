import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///golf_handicapper.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@golfhandicapper.com')

    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    UPLOAD_FOLDER   = os.path.join(os.path.dirname(__file__), 'golf_handicapper', 'static', 'img')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024   # 5 MB
    USERS_PER_PAGE  = 30
