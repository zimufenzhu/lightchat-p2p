import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 安全密钥：请使用 os.urandom(24) 或其他方式生成强密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A_SECURE_RANDOM_KEY_FOR_FLASK'
    # SQLite 用于开发环境
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis 配置 (用于用户状态映射)
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join('static', 'uploads', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB