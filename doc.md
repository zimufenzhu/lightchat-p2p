# LightChat P2P 开发文档

## 1. 项目概述

LightChat P2P 是一个基于 Flask 和 SocketIO 的实时聊天应用，支持用户注册、登录、一对一聊天、好友管理以及管理员功能。

### 1.1 主要功能

- **用户管理**：注册、登录、退出登录
- **实时聊天**：P2P 消息发送与接收
- **好友系统**：添加/删除好友、好友列表
- **会话管理**：聊天历史记录、清空聊天记录
- **管理员功能**：用户列表管理、删除用户、设置管理员权限

### 1.2 技术栈

| 类别 | 技术/库 | 版本 | 用途 |
|------|---------|------|------|
| 后端框架 | Flask | 3.0.3 | Web 服务器和路由管理 |
| 实时通信 | Flask-SocketIO | 5.3.6 | P2P 实时消息传输 |
| 数据库 ORM | Flask-SQLAlchemy | 3.1.1 | 数据库操作抽象 |
| 密码加密 | Flask-Bcrypt | 1.0.1 | 用户密码安全存储 |
| 环境变量 | python-dotenv | 1.0.1 | 配置管理 |
| 状态存储 | Redis | 5.0.1 | 用户连接状态管理 |
| Web 服务器 | eventlet | 0.35.2 | 高并发支持 |

## 2. 项目结构

```
lightchat_p2p/
├── app.py              # 主应用入口和路由定义
├── config.py           # 配置文件
├── models.py           # 数据库模型定义
├── requirements.txt    # 依赖列表
├── site.db            # SQLite 数据库文件
├── static/            # 静态资源
│   ├── css/           # 样式文件
│   │   └── tailwind.min.css  # Tailwind CSS 样式
│   ├── js/            # JavaScript 文件
│   │   └── client.js  # 前端逻辑
│   └── index.html     # 主页面
├── utils/             # 工具函数
│   └── redis_helpers.py  # Redis 操作封装
└── scripts/           # 辅助脚本
    ├── check_users.py   # 检查用户信息
    ├── set_admin.py     # 设置管理员用户
    ├── fix_admin.py     # 修复管理员权限
    └── init_db.py       # 初始化数据库
```

## 3. 安装与配置

### 3.1 环境要求

- Python 3.8 或更高版本
- Redis 服务器（可选，用于用户状态管理）

### 3.2 安装步骤

1. 克隆项目

```bash
git clone <repository-url>
cd lightchat_p2p
```

2. 创建虚拟环境

```bash
python -m venv venv
```

3. 激活虚拟环境

- Windows:
  ```bash
  venv\Scripts\activate
  ```

- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

4. 安装依赖

```bash
pip install -r requirements.txt
```

5. 配置环境变量

创建 `.env` 文件，添加以下内容（可选）：

```env
SECRET_KEY=your_secure_secret_key
REDIS_HOST=localhost
REDIS_PORT=6379
```

6. 初始化数据库

```bash
python init_db.py
```

7. 启动服务器

```bash
python app.py
```

服务器将在 `http://localhost:5001` 运行。

## 4. 核心功能模块

### 4.1 用户认证模块

#### 4.1.1 注册功能

- **路径**：`/api/register`
- **方法**：`POST`
- **参数**：
  - `username`：用户名（唯一）
  - `password`：密码
- **返回**：
  - 成功：`{"message": "注册成功"}`
  - 失败：`{"message": "错误信息"}`

#### 4.1.2 登录功能

- **路径**：`/api/login`
- **方法**：`POST`
- **参数**：
  - `username`：用户名
  - `password`：密码
- **返回**：
  - 成功：`{"message": "登录成功", "is_admin": true/false}`
  - 失败：`{"message": "错误信息"}`

#### 4.1.3 退出登录

- **路径**：`/api/logout`
- **方法**：`POST`
- **返回**：
  - 成功：`{"message": "退出成功"}`

### 4.2 聊天功能

#### 4.2.1 发送消息

- **事件**：`send_message`
- **参数**：
  - `receiver_id`：接收者用户 ID
  - `message`：消息内容

#### 4.2.2 接收消息

- **事件**：`receive_message`
- **参数**：
  - `sender_id`：发送者用户 ID
  - `sender_username`：发送者用户名
  - `message`：消息内容
  - `timestamp`：发送时间

#### 4.2.3 获取聊天历史

- **路径**：`/api/messages/<int:user_id>`
- **方法**：`GET`
- **返回**：
  - 成功：`[{"sender_id": 1, "content": "消息内容", "timestamp": "2023-01-01 12:00:00"}, ...]`
  - 失败：`{"message": "错误信息"}`

#### 4.2.4 清空聊天记录

- **路径**：`/api/messages/<int:user_id>`
- **方法**：`DELETE`
- **返回**：
  - 成功：`{"message": "聊天记录已清空"}`
  - 失败：`{"message": "错误信息"}`

### 4.3 好友系统

#### 4.3.1 获取好友列表

- **路径**：`/api/friends`
- **方法**：`GET`
- **返回**：
  - 成功：`[{"id": 1, "username": "user1"}, ...]`
  - 失败：`{"message": "错误信息"}`

#### 4.3.2 添加好友

- **路径**：`/api/friends`
- **方法**：`POST`
- **参数**：
  - `username`：要添加的用户名
- **返回**：
  - 成功：`{"message": "好友添加成功"}`
  - 失败：`{"message": "错误信息"}`

#### 4.3.3 删除好友

- **路径**：`/api/friends/<int:friend_id>`
- **方法**：`DELETE`
- **返回**：
  - 成功：`{"message": "好友删除成功"}`
  - 失败：`{"message": "错误信息"}`

### 4.4 管理员功能

#### 4.4.1 获取所有用户列表

- **路径**：`/api/admin/users`
- **方法**：`GET`
- **返回**：
  - 成功：`[{"id": 1, "username": "user1", "is_admin": false}, ...]`
  - 失败：`{"message": "错误信息"}`

#### 4.4.2 设置管理员权限

- **路径**：`/api/admin/users/<int:user_id>/admin`
- **方法**：`PUT`
- **参数**：
  - `is_admin`：true/false
- **返回**：
  - 成功：`{"message": "管理员权限设置成功"}`
  - 失败：`{"message": "错误信息"}`

#### 4.4.3 删除用户

- **路径**：`/api/admin/users/<int:user_id>`
- **方法**：`DELETE`
- **返回**：
  - 成功：`{"message": "用户删除成功"}`
  - 失败：`{"message": "错误信息"}`

## 5. 数据库结构

### 5.1 用户表 (User)

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY | 用户ID |
| username | String(20) | UNIQUE, NOT NULL | 用户名 |
| password_hash | String(60) | NOT NULL | 密码哈希 |
| is_admin | Boolean | DEFAULT False, NOT NULL | 是否为管理员 |

### 5.2 好友关系表 (Friendship)

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| user_a_id | Integer | PRIMARY KEY, FOREIGN KEY | 用户A的ID |
| user_b_id | Integer | PRIMARY KEY, FOREIGN KEY | 用户B的ID |
| status | String(10) | DEFAULT 'Accepted' | 好友关系状态 |
| created_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 5.3 会话表 (Conversation)

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY | 会话ID |
| user_one_id | Integer | FOREIGN KEY, NOT NULL | 用户1的ID |
| user_two_id | Integer | FOREIGN KEY, NOT NULL | 用户2的ID |
| last_message_at | DateTime | DEFAULT CURRENT_TIMESTAMP | 最后一条消息时间 |

### 5.4 消息表 (Message)

| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY | 消息ID |
| conversation_id | Integer | FOREIGN KEY, NOT NULL, INDEX | 所属会话ID |
| sender_id | Integer | FOREIGN KEY, NOT NULL | 发送者ID |
| content | Text | NOT NULL | 消息内容 |
| timestamp | DateTime | DEFAULT CURRENT_TIMESTAMP, INDEX | 发送时间 |
| is_read | Boolean | DEFAULT False | 是否已读 |

## 6. 核心 API 参考

### 6.1 用户认证相关 API

#### 6.1.1 注册

```
POST /api/auth/register
Content-Type: application/json

{
  "username": "new_user",
  "password": "password123"
}
```

#### 6.1.2 登录

```
POST /api/auth/login
Content-Type: application/json

{
  "username": "existing_user",
  "password": "password123"
}
```

#### 6.1.3 退出登录

```
POST /api/auth/logout
```

### 6.2 聊天相关 API

#### 6.2.1 获取聊天历史

```
GET /api/history/1  # 获取会话ID为1的聊天历史
```

#### 6.2.2 清空聊天记录

```
DELETE /api/history/1  # 清空会话ID为1的聊天记录
```

### 6.3 好友相关 API

#### 6.3.1 获取好友列表

```
GET /api/friends
```

#### 6.3.2 添加好友

```
POST /api/friends/add/new_friend
```

#### 6.3.3 删除好友

```
DELETE /api/friends/remove/2  # 删除ID为2的好友
```

### 6.4 管理员相关 API

#### 6.4.1 获取所有用户

```
GET /api/admin/users
```

#### 6.4.2 设置管理员权限

```
POST /api/admin/users/2/toggle-admin
```

#### 6.4.3 删除用户

```
DELETE /api/admin/users/2  # 删除ID为2的用户
```

## 7. SocketIO 事件

### 7.1 客户端发送事件

#### 7.1.1 `send_msg`

发送消息给另一个用户

```javascript
socket.emit('send_msg', {
  receiver_id: 2,
  content: 'Hello world'
});
```

### 7.2 客户端接收事件

#### 7.2.1 `receive_msg`

接收来自另一个用户的消息

```javascript
socket.on('receive_msg', (data) => {
  console.log(`Received message from ${data.sender_id}: ${data.content}`);
});
```



## 8. 常见问题与解决方案

### 8.1 端口冲突

如果遇到端口 5001 被占用的问题，可以使用以下命令查看并终止占用端口的进程：

- Windows:
  ```bash
  netstat -ano | findstr :5001
  taskkill /F /PID <PID>
  ```

- Linux/Mac:
  ```bash
  lsof -i :5001
  kill -9 <PID>
  ```

### 8.2 Tailwind CSS 加载错误

如果遇到 `net::ERR_BLOCKED_BY_ORB` 错误，可以将 CDN 链接替换为本地文件：

```html
<!-- 替换前 -->
<script src="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.js"></script>

<!-- 替换后 -->
<link href="/static/css/tailwind.min.css" rel="stylesheet">
```

### 8.3 管理员权限问题

如果需要设置管理员用户，可以使用 `set_admin.py` 脚本：

```bash
python set_admin.py
```

默认创建管理员用户名：`admin`，密码：`admin123456`

### 8.4 数据库重建

如果需要重置数据库，可以删除 `site.db` 文件并重新运行初始化脚本：

```bash
del site.db  # Windows
rm site.db   # Linux/Mac
python init_db.py
```

## 9. 开发指南

### 9.1 启动开发服务器

```bash
python app.py
```

### 9.2 调试模式

在 `app.py` 中设置 `debug=True` 以启用调试模式：

```python
if __name__ == '__main__':
    socketio.run(app, debug=True)
```

### 9.3 添加新功能

1. 在 `models.py` 中定义数据库模型（如果需要）
2. 在 `app.py` 中添加 API 路由
3. 在 `client.js` 中实现前端逻辑
4. 在 `index.html` 中添加 UI 元素

### 9.4 代码规范

- 使用 4 个空格进行缩进
- 遵循 PEP 8 规范（Python）
- 遵循 ESLint 规范（JavaScript）
- 为关键函数添加文档注释

## 10. 部署说明

### 10.1 生产环境配置

1. 设置 `debug=False`
2. 使用生产级 Web 服务器（如 Gunicorn）
3. 配置 HTTPS
4. 设置适当的 `SECRET_KEY`

### 10.2 使用 Gunicorn 部署

```bash
gunicorn -k eventlet -w 1 app:app
```

### 10.3 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 11. 更新日志

### 1.0.0 (2023-01-01)

- 初始版本发布
- 支持用户注册、登录、退出登录
- 支持实时 P2P 聊天
- 支持好友管理
- 支持管理员功能
- 支持聊天记录管理

## 12. 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 13. 许可证

MIT License

## 14. 联系方式

如有问题或建议，请通过以下方式联系：

- Email: example@example.com
- GitHub: [lightchat-p2p](https://github.com/example/lightchat-p2p)
