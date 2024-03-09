from redis.asyncio import Redis

from src.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB

auth_redis_db = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
