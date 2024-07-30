import redis

from .config import settings

redis_client = redis.Redis.from_url(settings.redis_url)


def get_cache(key: str):
    return redis_client.get(key)


def set_cache(key: str, value: str, expiration: int = 3600):
    redis_client.setex(key, expiration, value)
