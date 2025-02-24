import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLite 데이터베이스 파일 사용
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '이게 내 비밀 키야'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # SQLite 사용

# 🚀 SECRET_KEY 설정 (랜덤한 값으로 변경 가능)
SECRET_KEY = "chessjaeguksecretkey"  # 여기에 임의의 문자열을 입력해도 됨!