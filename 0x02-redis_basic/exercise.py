#!/usr/bin/env python3
'''A module for using the Redis data storage.
'''
import redis
import uuid
from typing import Callable, Union
from functools import wraps

# Count calls decorator
def count_calls(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = f"{method.__qualname__}"
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

# Call history decorator
def call_history(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store input
        self._redis.rpush(input_key, str(args))

        # Call the original method
        result = method(self, *args, **kwargs)

        # Store output
        self._redis.rpush(output_key, str(result))
        return result
    return wrapper

# Cache class definition
class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float, None]:
        data = self._redis.get(key)
        if data is not None and fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        return self.get(key, int)

    def replay(self, method: Callable):
        method_name = method.__qualname__
        inputs_key = f"{method_name}:inputs"
        outputs_key = f"{method_name}:outputs"
        inputs = self._redis.lrange(inputs_key, 0, -1)
        outputs = self._redis.lrange(outputs_key, 0, -1)

        print(f"{method_name} was called {len(inputs)} times:")
        for i, (input_data, output_data) in enumerate(zip(inputs, outputs)):
            print(f"{method_name}(*{input_data.decode('utf-8')}) -> {output_data.decode('utf-8')}")

# Sample usage
if __name__ == "__main__":
    cache = Cache()
    key = cache.store("hello")
    print(cache.get_str(key))
    cache.replay(cache.store)
