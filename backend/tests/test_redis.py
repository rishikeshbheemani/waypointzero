from app.memory.redis import check_redis_connection


def test_redis_connection():
    assert check_redis_connection() is True