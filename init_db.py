from app import app, db, User

# 使用应用上下文初始化数据库
with app.app_context():
    db.create_all()
    print("数据库初始化完成")
    print("User表结构:", [col.name for col in User.__table__.columns])
