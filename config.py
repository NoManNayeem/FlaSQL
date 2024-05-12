import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you_should_change_this')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///flasql.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
