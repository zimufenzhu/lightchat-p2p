from app import app, db, User

with app.app_context():
    # 将admin用户设置为管理员
    user = User.query.filter_by(username='admin').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"已将用户 {user.username} 设置为管理员")
    else:
        print("未找到admin用户")

    # 显示所有用户及其管理员状态
    users = User.query.all()
    print("\n所有用户列表：")
    for u in users:
        print(f"ID: {u.id}, 用户名: {u.username}, 管理员状态: {u.is_admin}")
