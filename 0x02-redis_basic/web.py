#!/usr/bin/env python3

import redis
import uuid
from typing import Union, Callable
from functools import wraps
import requests

redis_connection = redis.Redis()


def count_calls(method: Callable) -> Callable:
    """Count the number of calls to a function."""

    @wraps(method)
    def wrapper(url):
        """Wrapper function."""
        redis_connection.incr(f"count:{url}")

        result = method(url)
        redis_connection.setex(f"result:{url}", 10, result)

        return result

    return wrapper


def get_page(url: str) -> str:
    """Get the content of a web page."""
    return requests.get(url).text
