import redis

from app.config.settings import settings


client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def check_redis_connection() -> bool:
    return client.ping()