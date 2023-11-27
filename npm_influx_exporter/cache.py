from functools import wraps

from cachetools import TTLCache, cached

_cache = TTLCache(maxsize=128, ttl=3600)


def cached_with_ttl(cache: TTLCache | None = None):
    def decorator(func):
        @wraps(func)
        @cached(cache=cache or _cache)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
