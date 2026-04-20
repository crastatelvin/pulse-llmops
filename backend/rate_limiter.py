import asyncio
import time
from collections import defaultdict, deque


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str) -> bool:
        now = time.time()
        min_ts = now - self.window_seconds
        async with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] < min_ts:
                bucket.popleft()
            if len(bucket) >= self.limit:
                return False
            bucket.append(now)
            return True
