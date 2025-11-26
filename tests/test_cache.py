import pytest

from src.core.cache import cache_get, cache_set


@pytest.mark.asyncio
async def test_cache_set_get(fake_redis):
    """Тест запису та читання з кешу"""
    test_data = {"test": "data", "number": 123}

    result = await cache_set("test_key", test_data, 60)
    assert result is True

    cached_data = await cache_get("test_key")
    assert cached_data == test_data


@pytest.mark.asyncio
async def test_cache_get_nonexistent(fake_redis):
    """Тест читання неіснуючого ключа"""
    cached_data = await cache_get("nonexistent_key")
    assert cached_data is None


@pytest.mark.asyncio
async def test_cache_overwrite(fake_redis):
    """Тест перезапису ключа"""
    await cache_set("test_key", "first_value", 60)

    await cache_set("test_key", "second_value", 60)

    cached_data = await cache_get("test_key")
    assert cached_data == "second_value"
