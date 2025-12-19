from flask import Flask, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit, disconnect
from config import Config
from models import db, User, Conversation, Message, Friendship, bcrypt
from utils.redis_helpers import set_user_socket, get_user_socket, remove_user_socket
from datetime import datetime
import os
import uuid

# --- 初始化 ---
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt.init_app(app)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# --- 认证辅助函数 (简化) ---
def get_current_user_id():
    # ⚠️ 实际应从 JWT 或安全的 Session 中获取，此处简化为直接从 Session
    return session.get('user_id')

def get_current_user():
    user_id = get_current_user_id()
    if user_id:
        return User.query.get(user_id)
    return None

def is_admin():
    user = get_current_user()
    return user and user.is_admin

# --- 文件上传辅助函数 ---
# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- 辅助函数：查找或创建会话 ---
def get_or_create_conversation(user_one_id, user_two_id):
    # 确保 user_one_id < user_two_id 的顺序，方便查找
    u1, u2 = min(user_one_id, user_two_id), max(user_one_id, user_two_id)
    conv = Conversation.query.filter_by(user_one_id=u1, user_two_id=u2).first()
    if not conv:
        conv = Conversation(user_one_id=u1, user_two_id=u2)
        db.session.add(conv)
        db.session.commit()
    return conv

# --- 路由 ---

@app.route('/')
def index():
    return app.send_static_file('index.html')

# --- 图片上传路由 ---
@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    # 检查用户是否登录
    if not get_current_user_id():
        return jsonify({'message': 'User not authenticated'}), 401

    # 检查是否有文件上传
    if 'image' not in request.files:
        return jsonify({'message': 'No image file provided'}), 400

    file = request.files['image']
    
    # 检查文件是否有名称
    if file.filename == '':
        return jsonify({'message': 'No selected image file'}), 400

    # 检查文件类型是否允许
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not allowed'}), 400

    try:
        # 生成唯一文件名
        unique_filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        # 保存文件
        file.save(file_path)

        # 生成图片URL
        image_url = '/uploads/images/' + unique_filename

        return jsonify({'message': 'Image uploaded successfully', 'image_url': image_url}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to upload image', 'error': str(e)}), 500

# --- 静态文件路由 (用于访问上传的图片) ---
@app.route('/uploads/images/<filename>')
def uploaded_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id # 登录成功，存储到 Session
        return jsonify({'message': 'Login successful', 'user_id': user.id, 'username': user.username, 'is_admin': user.is_admin}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    # 检查是否是第一个用户
    is_first_user = User.query.count() == 0
    
    # 创建新用户
    user = User(username=data['username'])
    user.set_password(data['password'])
    
    # 如果是第一个用户，设置为管理员
    if is_first_user:
        user.is_admin = True
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'Registration successful', 'user_id': user.id, 'username': user.username}), 201

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None) # 从 Session 中移除用户 ID
    return jsonify({'message': 'Logout successful'}), 200

@app.route('/api/friends', methods=['GET'])
def get_friends():
    try:
        user_id = get_current_user_id()
        if not user_id: 
            return jsonify({'message': 'Unauthorized'}), 401

        # 获取用户的所有好友
        friends = []
        
        # 查询用户作为 user_a 的好友
        friendships_as_a = Friendship.query.filter_by(user_a_id=user_id, status='Accepted').all()
        for friendship in friendships_as_a:
            friends.append(friendship.user_b)
        
        # 查询用户作为 user_b 的好友
        friendships_as_b = Friendship.query.filter_by(user_b_id=user_id, status='Accepted').all()
        for friendship in friendships_as_b:
            friends.append(friendship.user_a)
        
        # 为每个好友获取会话信息
        results = []
        for friend in friends:
            try:
                # 获取会话
                conv = get_or_create_conversation(user_id, friend.id)
                
                # 获取最后一条消息
                last_message = Message.query.filter_by(conversation_id=conv.id).order_by(Message.timestamp.desc()).first()
                
                # 获取未读消息数
                unread_count = Message.query.filter_by(conversation_id=conv.id, is_read=False, sender_id=friend.id).count()
                
                # 安全地处理last_message为None的情况
                last_message_content = 'No messages yet.'
                if last_message is not None:
                    last_message_content = last_message.content if last_message.content else 'No messages yet.'
                
                results.append({
                    'conversation_id': conv.id,
                    'receiver_id': friend.id,
                    'receiver_name': friend.username,
                    'last_message_content': last_message_content,
                    'unread_count': unread_count
                })
            except Exception as e:
                # 即使某个朋友处理出错，也继续处理其他朋友
                continue
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500

@app.route('/api/friends/add/<username>', methods=['POST'])
def add_friend(username):
    user_id = get_current_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    # 查找要添加的用户
    friend_user = User.query.filter_by(username=username).first()
    if not friend_user: return jsonify({'message': 'User not found'}), 404
    
    # 不能添加自己
    if friend_user.id == user_id: return jsonify({'message': 'Cannot add yourself as friend'}), 400
    
    # 检查是否已经是好友 (更全面的检查)
    u1, u2 = min(user_id, friend_user.id), max(user_id, friend_user.id)
    existing_friendship = Friendship.query.filter(
        ((Friendship.user_a_id == u1) & (Friendship.user_b_id == u2)) |
        ((Friendship.user_a_id == u2) & (Friendship.user_b_id == u1))
    ).first()
    
    if existing_friendship:
        return jsonify({'message': 'Already friends'}), 400
    
    # 创建好友关系
    friendship = Friendship(user_a_id=u1, user_b_id=u2, status='Accepted')
    db.session.add(friendship)
    db.session.commit()
    
    # 创建会话
    get_or_create_conversation(user_id, friend_user.id)
    
    return jsonify({'message': 'Friend added successfully', 'friend_id': friend_user.id, 'friend_username': friend_user.username}), 200

@app.route('/api/friends/remove/<int:friend_id>', methods=['DELETE'])
def remove_friend(friend_id):
    user_id = get_current_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    # 查找好友关系
    u1, u2 = min(user_id, friend_id), max(user_id, friend_id)
    friendship = Friendship.query.filter_by(user_a_id=u1, user_b_id=u2).first()
    if not friendship: return jsonify({'message': 'Friendship not found'}), 404
    
    # 删除好友关系
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'message': 'Friend removed successfully'}), 200

@app.route('/api/history/<int:conversation_id>', methods=['GET'])
def get_history(conversation_id):
    user_id = get_current_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401

    # 简单分页，每次加载 50 条
    messages = Message.query.filter_by(conversation_id=conversation_id)\
                            .order_by(Message.timestamp.asc())\
                            .limit(50).all()\
    
    # 标记已读 (在加载历史记录时)
    Message.query.filter_by(conversation_id=conversation_id, is_read=False)\
                 .filter(Message.sender_id != user_id)\
                 .update({'is_read': True})
    db.session.commit()

    return jsonify([
        {'sender_id': msg.sender_id, 'content': msg.content, 'type': msg.type, 'timestamp': msg.timestamp.isoformat()}
        for msg in messages
    ])

@app.route('/api/history/<int:conversation_id>', methods=['DELETE'])
def clear_history(conversation_id):
    user_id = get_current_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    # 检查用户是否参与该会话
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'message': 'Conversation not found'}), 404
    
    if conversation.user_one_id != user_id and conversation.user_two_id != user_id:
        return jsonify({'message': 'You are not part of this conversation'}), 403
    
    # 删除该会话的所有消息
    Message.query.filter_by(conversation_id=conversation_id).delete()
    db.session.commit()
    
    return jsonify({'message': 'Chat history cleared successfully'}), 200

# --- 管理员路由 ---
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # 检查是否为管理员
    if not is_admin():
        return jsonify({'message': 'Unauthorized'}), 401
    
    # 获取所有用户信息
    users = User.query.all()
    return jsonify([
        {
            'id': user.id,
            'username': user.username,
            'is_admin': user.is_admin
        }
        for user in users
    ]), 200

@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
def toggle_admin(user_id):
    # 检查是否为管理员
    if not is_admin():
        return jsonify({'message': 'Unauthorized'}), 401
    
    # 不能修改自己的管理员状态
    current_user = get_current_user()
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot modify your own admin status'}), 400
    
    # 查找用户并切换管理员状态
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'message': 'Admin status updated successfully',
        'user_id': user.id,
        'is_admin': user.is_admin
    }), 200

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # 检查是否为管理员
    if not is_admin():
        return jsonify({'message': 'Unauthorized'}), 401
    
    # 不能删除自己
    current_user = get_current_user()
    if current_user.id == user_id:
        return jsonify({'message': 'Cannot delete your own account'}), 400
    
    # 查找用户
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # 删除与该用户相关的所有消息
    Message.query.filter(Message.sender_id == user_id).delete()
    Message.query.filter(Message.receiver_id == user_id).delete()
    
    # 删除与该用户相关的所有好友关系
    friendships = Friendship.query.filter(
        (Friendship.user_a_id == user_id) | (Friendship.user_b_id == user_id)
    ).all()
    for friendship in friendships:
        db.session.delete(friendship)
    
    # 删除与该用户相关的所有会话
    conversations = Conversation.query.filter(
        (Conversation.user_one_id == user_id) | (Conversation.user_two_id == user_id)
    ).all()
    for conversation in conversations:
        db.session.delete(conversation)
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

# --- 全局错误处理 ---
@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理，确保所有API错误返回JSON响应"""
    if request.path.startswith('/api/'):
        # 如果是API请求，返回JSON错误响应
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500
    # 非API请求返回默认错误页面
    return app.handle_exception(e)

# --- SocketIO 事件处理 (P2P 核心) ---

@socketio.on('connect')
def handle_connect():
    # ⚠️ 必须确保用户已经登录，这里从 Session 中获取 user_id
    user_id = session.get('user_id') 
    if user_id is None:
        # 如果未认证，断开连接
        disconnect()
        return False
    
    # 存储用户ID和Socket ID的映射
    set_user_socket(user_id, request.sid)
    # 存储反向映射，便于 disconnect 时查询 user_id (可选优化)
    # redis_client.set(f"sid:{request.sid}", user_id, ex=SOCKET_TTL)


@socketio.on('disconnect')
def handle_disconnect():
    # ⚠️ 依赖于反向映射或在 connect 时将 user_id 存储在 SocketIO session
    # 假设我们能在 disconnect 时获取 user_id
    user_id = session.get('user_id') 
    if user_id:
        remove_user_socket(user_id)

@socketio.on('send_msg')
def handle_send_message(data):
    sender_id = get_current_user_id()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    message_type = data.get('type', 'text')  # 默认文本类型
    
    if not sender_id or not receiver_id or not content:
        return
        
    # 1. 查找或创建会话
    conv = get_or_create_conversation(sender_id, receiver_id)
    
    # 2. 消息持久化
    new_message = Message(
        conversation_id=conv.id, 
        sender_id=sender_id, 
        content=content,
        type=message_type,  # 添加消息类型
        is_read=False # 默认未读
    )
    db.session.add(new_message)
    # 更新会话最后消息时间
    conv.last_message_at = datetime.utcnow()
    db.session.commit()
    
    # 组装完整的消息 DTO
    message_dto = {
        'conversation_id': conv.id,
        'sender_id': sender_id,
        'content': content,
        'type': message_type,  # 添加消息类型到DTO
        'timestamp': new_message.timestamp.isoformat()
    }

    # 3. 实时定向传输 (P2P)
    receiver_sid = get_user_socket(receiver_id)
    
    # 发送给接收方
    if receiver_sid:
        emit('receive_msg', message_dto, to=receiver_sid)
        # 标记已读 (如果用户在线，可以假设消息被接收即已读，但通常在前端确认)
        new_message.is_read = True 
        db.session.commit()
        
    # 4. 发送给发送方 (本地确认)
    emit('receive_msg', message_dto, to=request.sid)

# --- 启动 ---
if __name__ == '__main__':
    with app.app_context():
        # ⚠️ 首次运行或需要重置数据库时取消注释
        # db.drop_all()
        db.create_all()
        
        # ⚠️ 创建测试用户 (首次运行时)
        if not User.query.first():
            user1 = User(username='userA')
            user1.set_password('123')
            user2 = User(username='userB')
            user2.set_password('123')
            db.session.add_all([user1, user2])
            db.session.commit()
            
            # 建立好友关系
            u1, u2 = min(user1.id, user2.id), max(user1.id, user2.id)
            friendship = Friendship(user_a_id=u1, user_b_id=u2, status='Accepted')
            db.session.add(friendship)
            db.session.commit()
            
            # 创建会话
            get_or_create_conversation(user1.id, user2.id)

    # 使用 socketio.run() 启动服务器，使用端口5001避免冲突
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)