import os
from datetime import timedelta

SECRET_KEY = 'your-secret-key-change-this-in-production'
SQLALCHEMY_DATABASE_URI = 'sqlite:///news.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
PERMANENT_SESSION_LIFETIME = timedelta(hours=2)