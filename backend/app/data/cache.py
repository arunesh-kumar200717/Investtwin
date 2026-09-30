from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any


@dataclass
class CacheEntry:
    value: Any
    fetched_at: datetime
    expires_at: datetime


class MemoryDataCache:
    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> CacheEntry | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry.expires_at > datetime.now(timezone.utc):
                return entry
            if entry:
                self._entries.pop(key, None)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> CacheEntry:
        now = datetime.now(timezone.utc)
        entry = CacheEntry(value=value, fetched_at=now, expires_at=now + timedelta(seconds=ttl_seconds))
        with self._lock:
            self._entries[key] = entry
        return entry


market_data_cache = MemoryDataCache()