from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ()


class IntegrationClient:
    def __init__(self, channel: grpc.Channel):
        self.channel = channel
