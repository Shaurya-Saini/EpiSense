"""Thread-safe in-memory data store for sensor readings."""

from collections import deque
from threading import Lock
from typing import List, Dict, Any


class DataStore:
    """In-memory store backed by a deque with a fixed max size."""

    def __init__(self, max_size: int = 100):
        self._readings: deque = deque(maxlen=max_size)
        self._lock = Lock()
        self._counter = 0

    def add_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new reading and return it with an assigned ID."""
        with self._lock:
            self._counter += 1
            reading["id"] = self._counter
            self._readings.append(reading)
            return reading

    def get_readings(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent readings, up to `limit`."""
        with self._lock:
            items = list(self._readings)
            return items[-limit:][::-1]  # Most recent first

    def get_latest(self) -> Dict[str, Any] | None:
        """Return the most recent reading, or None if empty."""
        with self._lock:
            return self._readings[-1] if self._readings else None


# Singleton instance used across the application
store = DataStore()
