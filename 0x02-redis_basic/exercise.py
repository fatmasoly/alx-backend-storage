#!/usr/bin/env python3
"""Redis basic exercise."""

import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(func: Callable) -> Callable:
    """Count the number of calls to a function."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """Wrapper function."""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(func.__qualname__)

        return func(self, *args, **kwargs)

    return wrapper


class Cache:
    def __init__(self) -> None:
        """Initialize the cache."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in the cache and return a key for it."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Union[Callable, None] = None) -> str:
        """Get the data from the cache using the key."""
        value = self._redis.get(key)

        if fn:
            return fn(value)

        return value

    def get_str(self, key: str) -> str:
        """Get the data from the cache using the key."""
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Get the data from the cache using the key."""
        return self.get(key, int)
