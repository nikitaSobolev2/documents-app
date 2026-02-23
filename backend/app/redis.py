from typing import Generator

from redis import Redis

from app.config import config

redis_client = Redis.from_url(config.REDIS_URL, decode_responses=True)


def get_redis() -> Generator[Redis, None, None]:
    yield redis_client
