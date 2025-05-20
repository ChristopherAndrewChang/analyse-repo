from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import timezone
from django.conf import settings

if TYPE_CHECKING:
    from datetime import datetime
    from google.protobuf.timestamp_pb2 import Timestamp
    from google.protobuf.duration_pb2 import Duration


__all__ = ("timestamp_to_datetime",)


def timestamp_to_datetime(timestamp: Timestamp) -> datetime:
    return timestamp.ToDatetime(
        tzinfo=timezone.utc if settings.USE_TZ else None)
