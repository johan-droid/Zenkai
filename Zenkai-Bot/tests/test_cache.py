import pytest

from zenkai.core.cache import MemoryCache, NullCache, RedisCache


@pytest.mark.asyncio
async def test_memory_cache_respects_expiration() -> None:
    cache = MemoryCache()

    await cache.set_json("key", {"value": 1}, ttl_seconds=1)
    assert await cache.get_json("key") == {"value": 1}

    await cache.set("empty", "value", ttl_seconds=0)
    assert await cache.get("empty") is None

    with pytest.raises(ValueError, match="ttl_seconds"):
        await cache.set("negative", "value", ttl_seconds=-1)

    await cache.delete("empty")
    assert await cache.get("empty") is None

    await cache.close()


@pytest.mark.asyncio
async def test_null_cache_supports_json_api() -> None:
    cache = NullCache()

    await cache.set_json("key", {"value": 1})

    assert await cache.get_json("key") is None


@pytest.mark.asyncio
async def test_set_json_serializes_value_for_every_implementation() -> None:
    written: list[tuple[str, str]] = []

    async def spy_set(key: str, value: str, ttl_seconds: int | None = None) -> None:
        written.append((key, value))

    for implementation in (NullCache(), object.__new__(RedisCache)):
        written.clear()
        implementation.set = spy_set  # type: ignore[method-assign]
        await implementation.set_json("key", {"value": 1})
        assert written == [("key", '{"value": 1}')], implementation

    cache = MemoryCache()
    await cache.set_json("key", {"value": 1})
    assert await cache.get_json("key") == {"value": 1}


@pytest.mark.asyncio
async def test_redis_cache_deletes_for_zero_ttl() -> None:
    class FakeRedis:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str, str | None]] = []

        async def set(self, key: str, value: str, ex: int | None = None) -> None:
            self.calls.append(("set", key, ex))

        async def delete(self, key: str) -> None:
            self.calls.append(("delete", key, None))

    cache = object.__new__(RedisCache)
    fake = FakeRedis()
    cache._client = fake

    await cache.set("key", "value", ttl_seconds=0)

    assert fake.calls == [("delete", "key", None)]
