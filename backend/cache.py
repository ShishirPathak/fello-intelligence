# Cache helpers for company enrichment data using Redis or an in-memory fallback.
from __future__ import annotations

import json
import os
import time
from typing import Any

from redis import asyncio as redis

CACHE_TTL_SECONDS = 86400
_CACHE_PREFIX = "fello:company:"
_memory_cache: dict[str, tuple[float, dict[str, Any]]] = {}


def _cache_key(domain: str) -> str:
    return f"{_CACHE_PREFIX}{domain.strip().lower()}"


def _get_redis_client() -> redis.Redis | None:
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None

    try:
        return redis.from_url(redis_url, decode_responses=True)
    except Exception:
        return None


async def get_cached_profile(domain: str) -> dict[str, Any] | None:
    normalized_domain = domain.strip().lower()
    if not normalized_domain:
        return None

    client = _get_redis_client()
    if client is not None:
        try:
            cached_value = await client.get(_cache_key(normalized_domain))
            if cached_value:
                return json.loads(cached_value)
        except Exception:
            pass

    cached_entry = _memory_cache.get(normalized_domain)
    if not cached_entry:
        return None

    expires_at, payload = cached_entry
    if expires_at <= time.time():
        _memory_cache.pop(normalized_domain, None)
        return None

    return payload


async def set_cached_profile(domain: str, data: dict[str, Any]) -> None:
    normalized_domain = domain.strip().lower()
    if not normalized_domain:
        return

    client = _get_redis_client()
    if client is not None:
        try:
            await client.set(
                _cache_key(normalized_domain),
                json.dumps(data),
                ex=CACHE_TTL_SECONDS,
            )
            return
        except Exception:
            pass

    _memory_cache[normalized_domain] = (time.time() + CACHE_TTL_SECONDS, data)
