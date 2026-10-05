import json
import time
from typing import Any, Protocol, cast

from redis.asyncio import Redis


class Cache(Protocol):
    async def get(self, key: str) -> str | None: ...

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None: ...

    async def get_json(self, key: str) -> Any: ...

    async def set_json(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> None: ...

    async def delete(self, key: str) -> None: ...

    async def close(self) -> None: ...


class MemoryCache:
    def __init__(self) -> None:
        self._values: dict[str, tuple[float | None, str]] = {}

    async def get(self, key: str) -> str | None:
        item = self._values.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at is not None and expires_at <= time.monotonic():
            self._values.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is not None and ttl_seconds < 0:
            raise ValueError("ttl_seconds cannot be negative")
        if ttl_seconds == 0:
            self._values.pop(key, None)
            return
        expires_at = time.monotonic() + ttl_seconds if ttl_seconds is not None else None
        self._values[key] = (expires_at, value)

    async def get_json(self, key: str) -> Any:
        value = await self.get(key)
        return json.loads(value) if value is not None else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        await self.set(key, json.dumps(value), ttl_seconds)

    async def delete(self, key: str) -> None:
        self._values.pop(key, None)

    async def close(self) -> None:
        self._values.clear()


class NullCache:
    async def get(self, key: str) -> str | None:
        return None

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is not None and ttl_seconds < 0:
            raise ValueError("ttl_seconds cannot be negative")
        return None

    async def get_json(self, key: str) -> Any:
        return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        await self.set(key, json.dumps(value), ttl_seconds)

    async def delete(self, key: str) -> None:
        return None

    async def close(self) -> None:
        return None


class RedisCache:
    def __init__(self, url: str) -> None:
        self._client = Redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return cast(str | None, await self._client.get(key))

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is not None and ttl_seconds < 0:
            raise ValueError("ttl_seconds cannot be negative")
        if ttl_seconds == 0:
            await self.delete(key)
            return
        await self._client.set(key, value, ex=ttl_seconds)

    async def get_json(self, key: str) -> Any:
        value = await self.get(key)
        return json.loads(value) if value is not None else None

    async def set_json(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        await self.set(key, json.dumps(value), ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def close(self) -> None:
        await self._client.aclose()


def build_cache(url: str | None) -> Cache:
    return RedisCache(url) if url else MemoryCache()
