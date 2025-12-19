from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False) # 添加管理员权限字段
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # 好友关系的反向引用
    friendships_a = db.relationship('Friendship', foreign_keys='Friendship.user_a_id', backref='user_a', lazy=True)
    friendships_b = db.relationship('Friendship', foreign_keys='Friendship.user_b_id', backref='user_b', lazy=True)

class Friendship(db.Model):
    # 强制 user_a_id < user_b_id 保证唯一性
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    status = db.Column(db.String(10), default='Accepted') # 简化，假设已是好友
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # 添加创建时间
    
class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_one_id 和 user_two_id 必须是 Friendship 中的 a/b
    user_one_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_two_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 级联删除消息
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan', lazy='dynamic')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id', ondelete='CASCADE'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(10), default='text', nullable=False)  # 添加消息类型字段
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_read = db.Column(db.Boolean, default=False)