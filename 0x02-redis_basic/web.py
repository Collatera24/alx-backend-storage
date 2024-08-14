#!/usr/bin/env python3
'''A module for using the Redis data storage.
'''
import requests
import redis
from typing import Callable

class WebCache:
    def __init__(self):
        self._redis = redis.Redis()
    
    def get_page(self, url: str) -> str:
        cached_page = self._redis.get(f"cache:{url}")
        if cached_page:
            return cached_page.decode('utf-8')
        
        response = requests.get(url)
        page_content = response.text

        self._redis.setex(f"cache:{url}", 10, page_content)
        self._redis.incr(f"count:{url}")
        return page_content

# Sample usage
if __name__ == "__main__":
    web_cache = WebCache()
    url = "http://slowwly.robertomurray.co.uk/delay/3000/url/https://www.google.com"
    print(web_cache.get_page(url))
