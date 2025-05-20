from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from functools import wraps

from idvalid_integration._settings import integration_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("auto_channel",)


def auto_channel(*, setting_name):
    def handle(func):
        @wraps(func)
        def wrapper(
                *args,
                channel: grpc.Channel = None,
                credentials: grpc.ChannelCredentials = None,
                options: tuple = None,
                compression: grpc.Compression = None,
                **kwargs):
            if channel:
                return func(channel, *args, **kwargs)
            if credentials:
                channel = grpc.secure_channel(
                    getattr(integration_settings, setting_name), credentials,
                    options=options, compression=compression)
            else:
                channel = grpc.insecure_channel(
                    getattr(integration_settings, setting_name),
                    options=options, compression=compression)
            with channel:
                return func(channel, *args, **kwargs)
        return wrapper
    return handle
