from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.http.request import HttpRequest


__all__ = ("get_client_ip",)


def get_client_ip(request: HttpRequest | Request) -> str | None:
    # Check for the IP address in X-Forwarded-For header
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can have multiple IPs, the client IP is the first one
        return x_forwarded_for.split(',')[0]
    else:
        # Fallback to remote address
        return request.META.get('REMOTE_ADDR')
