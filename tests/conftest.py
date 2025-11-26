import asyncio
import os

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from src.main import app

os.environ["TESTING"] = "1"


@pytest.fixture(scope="session")
def client():
    """Тестовий клієнт для FastAPI"""
    return TestClient(app)


@pytest.fixture
def fake_redis(monkeypatch):
    """Фейковий Redis для тестування кешу"""
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr("src.core.redis_client.get_redis", lambda: redis)

    return redis


@pytest.fixture(scope="session")
def event_loop():
    """Фікстура для асинхронних тестів"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
