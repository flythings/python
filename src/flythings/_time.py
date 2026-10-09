import time
from datetime import datetime
from typing import TypeAlias

Timestamp: TypeAlias = int | float | datetime
"""Epoch milliseconds, or a `datetime` (naive values are read as local time, like `datetime.timestamp`)."""


def to_millis(value: Timestamp) -> int:
    if isinstance(value, datetime):
        return round(value.timestamp() * 1000)
    return int(value)


def now_millis() -> int:
    return round(time.time() * 1000)
