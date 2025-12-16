from models import db, User
from app import app

def set_admin_user():
    with app.app_context():
        # 检查是否已经存在管理员用户
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print(f"已经存在管理员用户: {existing_admin.username} (ID: {existing_admin.id})")
            return
        
        # 检查是否已经存在名为admin的用户
        existing_user = User.query.filter_by(username='admin').first()
        if existing_user:
            # 如果存在，将其设置为管理员
            existing_user.is_admin = True
            db.session.commit()
            print(f"已将现有用户 {existing_user.username} (ID: {existing_user.id}) 设置为管理员")
        else:
            # 创建新的管理员用户
            admin_user = User(username='admin', is_admin=True)
            admin_user.set_password('admin123456')
            db.session.add(admin_user)
            db.session.commit()
            print(f"已创建管理员用户: admin (ID: {admin_user.id})")

if __name__ == "__main__":
    set_admin_user()
