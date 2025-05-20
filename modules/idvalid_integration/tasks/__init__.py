from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from celery import Celery
    from celery.result import AsyncResult


__all__ = ("call_task",)


def call_task(*args, app: Celery = None, **kwargs) -> AsyncResult:
    if app is None:
        from celery import current_app
        app = current_app
    return app.send_task(*args, **kwargs)
