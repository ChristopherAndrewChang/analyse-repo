from __future__ import annotations
from typing import TYPE_CHECKING

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration

if TYPE_CHECKING:
    from datetime import datetime, timedelta


__all__ = ("datetime_to_message", "timedelta_to_message")


def datetime_to_message(value: datetime | None) -> Timestamp:
    result = Timestamp()
    if value is None:
        return result
    result.FromDatetime(value)
    return result


def timedelta_to_message(value: timedelta | None) -> Duration:
    result = Duration()
    if value is None:
        return result
    result.FromTimedelta(value)
    return result
