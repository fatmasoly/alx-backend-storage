#!/usr/bin/env python3
"""Redis basic exercise."""

import redis
import uuid
from typing import Union


class Cache:
    def __init__(self) -> None:
        """Initialize the cache."""
        self._redis = redis.Redis()
        self._redis = self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in the cache and return a key for it."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
