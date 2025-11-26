import os

from redis import asyncio as aioredis


def get_redis() -> aioredis.Redis:
    """Підключення до Upstash Redis"""
    redis_url = os.getenv("REDIS_URL")
    return aioredis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        ssl_cert_reqs=None,  # Вимкнути перевірку SSL для Upstash
    )
