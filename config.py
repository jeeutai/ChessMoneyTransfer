import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '이게 내 비밀 키야'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # SQLite 사용
