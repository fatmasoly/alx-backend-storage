#!/usr/bin/env python3
"""Redis basic exercise."""

import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Count the number of calls to a function."""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function."""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)

        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Keep a history of the calls made to a function."""

    @wraps(method)
    def wrapper(self, *args, **kwds):
        """Wrapper function for the decorated method."""
        key = method(self, *args, **kwds)

        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(f"{method.__qualname__}:inputs", str(args))
            self._redis.rpush(f"{method.__qualname__}:outputs", key)

        return key

    return wrapper


def replay(fn: Callable) -> None:
    """Replay the history of calls of a function."""
    redis_obj = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_obj, redis.Redis):
        return

    method_name = fn.__qualname__
    inputs_name = method_name + ':inputs'
    outputs_name = method_name + ':outputs'

    inputs_list = redis_obj.lrange(inputs_name, 0, -1)
    outputs_list = redis_obj.lrange(outputs_name, 0, -1)

    counts = redis_obj.get(method_name).decode('utf-8')

    print(f"{method_name} was called {counts} times:")

    for input, output in zip(inputs_list, outputs_list):
        print(f"{method_name}(*{input.decode('utf-8')}) -> {output}")


class Cache:
    def __init__(self) -> None:
        """Initialize the cache."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
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
