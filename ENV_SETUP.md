# 环境依赖配置指南

## 1. Python 版本要求
- **推荐版本**: Python 3.12.10
- **兼容版本**: Python 3.10 及以上

## 2. 依赖包安装

### 2.1 安装所有依赖
```bash
pip install -r requirements.txt
```

### 2.2 依赖包列表
| 包名 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.3 | Web框架 |
| Flask-SocketIO | 5.3.6 | 实时通信支持 |
| Flask-SQLAlchemy | 3.1.1 | 数据库ORM |
| Flask-Bcrypt | 1.0.1 | 密码加密 |
| python-dotenv | 1.0.1 | 环境变量加载 |
| redis | 5.0.1 | 用户状态存储 |
| eventlet | 0.35.2 | 异步通信支持 |

## 3. 环境配置

### 3.1 创建 `.env` 文件（可选但推荐）
在项目根目录创建 `.env` 文件，添加以下配置：

```env
# 安全密钥：请使用 os.urandom(24) 或其他方式生成强密钥
SECRET_KEY=your_secure_random_key_here

# Redis 配置（可选，使用默认值可忽略）
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 3.2 数据库配置
- 默认使用 SQLite 数据库（`site.db`）
- 无需额外配置，启动时自动创建
- 如需使用其他数据库，修改 `config.py` 中的 `SQLALCHEMY_DATABASE_URI`

### 3.3 Redis 服务
- 项目依赖 Redis 用于用户状态管理
- 安装 Redis：
  - Windows: https://github.com/microsoftarchive/redis/releases
  - Linux: `sudo apt-get install redis-server`
  - macOS: `brew install redis`
- 启动 Redis 服务：
  - Windows: `redis-server.exe`
  - Linux/macOS: `redis-server`

## 4. 项目初始化

### 4.1 初始化数据库
```bash
python -c "from app import app, db; with app.app_context(): db.create_all()"
```

### 4.2 创建管理员账户
```bash
python set_admin.py
```
- 默认管理员账号：`admin`
- 默认管理员密码：`admin123456`

## 5. 启动项目

### 5.1 开发模式
```bash
python app.py
```

### 5.2 SocketIO 模式
```bash
python -m flask run --host=0.0.0.0 --port=5001
```

### 5.3 生产模式（推荐使用 Gunicorn）
```bash
pip install gunicorn

# 使用 eventlet worker
gunicorn -k eventlet -b 0.0.0.0:5001 app:app
```

## 6. 访问项目
- 打开浏览器访问：`http://localhost:5001`
- 使用管理员账号登录：`admin` / `admin123456`

## 7. 常见问题

### 7.1 Redis 连接失败
- 确保 Redis 服务正在运行
- 检查 `config.py` 中的 Redis 配置
- 尝试重启 Redis 服务

### 7.2 端口被占用
```bash
# Windows
netstat -ano | findstr :5001
taskkill /F /PID <进程ID>

# Linux/macOS
lsof -i :5001
kill -9 <进程ID>
```

### 7.3 数据库错误
- 删除 `site.db` 文件
- 重新执行数据库初始化命令

## 8. 其他配置

### 8.1 修改端口
在 `app.py` 文件末尾修改端口：
```python
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)  # 修改此处的端口号
```

### 8.2 修改异步模式
在 `app.py` 文件中修改 SocketIO 初始化：
```python
# 使用 eventlet（推荐）
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# 或使用 gevent
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins="*")

# 或使用 threading（不推荐用于生产环境）
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")
```

---

**注意**: 在生产环境中，请确保：
1. 使用强密钥替换默认的 `SECRET_KEY`
2. 禁用调试模式
3. 配置适当的 CORS 设置
4. 使用 HTTPS 加密连接
5. 定期备份数据库文件
