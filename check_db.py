from app import app, db, User, Friendship

with app.app_context():
    # 检查所有用户
    users = User.query.all()
    print("Users:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Admin: {user.is_admin}")
    
    # 检查所有好友关系
    print("\nFriendships:")
    friendships = Friendship.query.all()
    for friendship in friendships:
        print(f"{friendship.user_a_id} - {friendship.user_b_id} (Status: {friendship.status})")
    
    # 检查会话
    from models import Conversation
    print("\nConversations:")
    conversations = Conversation.query.all()
    for conv in conversations:
        print(f"ID: {conv.id}, User1: {conv.user_one_id}, User2: {conv.user_two_id}")