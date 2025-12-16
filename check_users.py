from models import db, User
from app import app

with app.app_context():
    # 查询所有用户
    users = User.query.all()
    
    print("数据库中的账号信息：")
    print("-" * 40)
    print("ID	用户名		是否管理员")
    print("-" * 40)
    
    for user in users:
        print(f"{user.id}	{user.username}		{'是' if user.is_admin else '否'}")
    
    print("-" * 40)
    print(f"总计：{len(users)}个用户")
