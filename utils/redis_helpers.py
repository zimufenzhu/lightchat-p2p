import redis
from config import Config
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试初始化 Redis 客户端
redis_client = None
try:
    redis_client = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0, decode_responses=True)
    # 测试连接
    redis_client.ping()
    logger.info("Redis连接成功")
except Exception as e:
    logger.warning(f"Redis连接失败: {e}")
    logger.info("使用内存存储替代Redis")
    # 使用内存存储替代Redis
    redis_client = {}

# TTL (Time To Live) in seconds for socket mapping
SOCKET_TTL = 3600 

def set_user_socket(user_id, sid):
    """绑定用户ID到当前Socket ID"""
    try:
        if hasattr(redis_client, 'set'):
            redis_client.set(f"user:{user_id}", sid, ex=SOCKET_TTL)
        else:
            # 使用内存存储
            redis_client[f"user:{user_id}"] = sid
    except Exception as e:
        logger.error(f"设置用户Socket失败: {e}")

def get_user_socket(user_id):
    """通过用户ID获取Socket ID"""
    try:
        if hasattr(redis_client, 'get'):
            return redis_client.get(f"user:{user_id}")
        else:
            # 使用内存存储
            return redis_client.get(f"user:{user_id}")
    except Exception as e:
        logger.error(f"获取用户Socket失败: {e}")
        return None

def remove_user_socket(user_id):
    """移除用户的绑定状态"""
    try:
        if hasattr(redis_client, 'delete'):
            redis_client.delete(f"user:{user_id}")
        else:
            # 使用内存存储
            if f"user:{user_id}" in redis_client:
                del redis_client[f"user:{user_id}"]
    except Exception as e:
        logger.error(f"移除用户Socket失败: {e}")
    
# ⚠️ 注意：实际应用中，还需要一个 sid -> user_id 的反向映射以便在 disconnect 时查询。
# 为简化，我们在 connect 时将 user_id 存储在 Flask Session 中，或使用反向映射。