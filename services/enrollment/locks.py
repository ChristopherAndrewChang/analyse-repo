from __future__ import annotations

import logging
import time

from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.core.cache import caches, DEFAULT_CACHE_ALIAS
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.functional import cached_property

if TYPE_CHECKING:
    from typing import Any, Self
    from django.core.cache.backends.base import BaseCache


logger = logging.getLogger(__name__)
__all__ = ("CacheLockContext", "Timeout", "CacheLock")


@dataclass
class CacheLockContext:
    """A dataclass which holds the context for a ``CacheLock`` object."""

    #: The path to the lock file.
    lock_key: str

    #: The default timeout value.
    timeout: int

    #: Whether the lock should be blocking or not
    blocking: bool

    client: str | BaseCache

    cache_timeout: int

    #: The lock counter is used for implementing the nested locking mechanism.
    lock_counter: int = 0  # When the lock is acquired is increased and the lock is only released, when this value is 0

    success: bool = False


class Timeout(TimeoutError):  # noqa: N818
    """Raised when the lock could not be acquired in *timeout* seconds."""

    def __init__(self, lock_key: str) -> None:
        super().__init__()
        self._lock_key = lock_key

    def __reduce__(self) -> str | tuple[Any, ...]:
        return self.__class__, (self._lock_key,)  # Properly pickle the exception

    def __str__(self) -> str:
        return f"The file lock '{self._lock_key}' could not be acquired."

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.lock_file!r})"

    @property
    def lock_file(self) -> str:
        """:return: The path of the file lock."""
        return self._lock_key


class CacheLock:
    def __init__(
            self, lock_key: str, *,
            timeout: int = 10,
            blocking: bool = True,
            client: str | BaseCache = None,
            cache_timeout: int = DEFAULT_TIMEOUT):

        if client is None:
            client = caches[DEFAULT_CACHE_ALIAS]

        kwargs: dict[str, "Any"] = {
            "lock_file": lock_key,
            "timeout": timeout,
            "blocking": blocking,
            "client": client,
            "cache_timeout": cache_timeout,
        }
        self._context = CacheLockContext(**kwargs)

    @property
    def lock_key(self) -> str:
        return self._context.lock_key

    @property
    def timeout(self) -> float:
        return self._context.timeout

    @timeout.setter
    def timeout(self, value: int | str) -> None:
        self._context.timeout = int(value)

    @property
    def blocking(self) -> bool:
        return self._context.blocking

    @blocking.setter
    def blocking(self, value: bool) -> None:
        self._context.blocking = value

    @cached_property
    def client(self) -> BaseCache:
        _client = self._context.client
        if _client is None:
            return caches[DEFAULT_CACHE_ALIAS]
        if isinstance(_client, str):
            return caches[_client]
        return _client

    @property
    def cache_timeout(self) -> int:
        return self._context.cache_timeout

    @cache_timeout.setter
    def cache_timeout(self, value: int):
        self._context.cache_timeout = value

    @property
    def lock_counter(self) -> int:
        return self._context.lock_counter

    @property
    def is_locked(self) -> bool:
        return self._context.success

    def _acquire(self):
        if self.client.add(self.lock_key, True, self.cache_timeout):
            self._context.success = True

    def acquire(
        self, *,
        timeout: int | None = None,
        poll_interval: float = 0.05,
        blocking: bool | None = None,
    ) -> Self:
        # Use the default timeout, if no timeout is provided.
        if timeout is None:
            timeout = self._context.timeout
        else:
            timeout = int(timeout)

        if blocking is None:
            blocking = self._context.blocking

        # Increment the number right at the beginning. We can still undo it, if something fails.
        self._context.lock_counter += 1

        lock_id = id(self)
        lock_key = self.lock_key
        start_time = time.perf_counter()
        try:
            while True:
                if not self.is_locked:
                    logger.debug("Attempting to acquire lock %s on %s", lock_id, lock_key)
                    self._acquire()

                if self.is_locked:
                    logger.debug("Lock %s acquired on %s", lock_id, lock_key)
                    break

                if blocking is False:
                    logger.debug("Failed to immediately acquire lock %s on %s", lock_id, lock_key)
                    raise Timeout(lock_key)  # noqa: TRY301

                if 0 <= timeout < time.perf_counter() - start_time:
                    logger.debug("Timeout on acquiring lock %s on %s", lock_id, lock_key)
                    raise Timeout(lock_key)  # noqa: TRY301

                msg = "Lock %s not acquired on %s, waiting %s seconds ..."
                logger.debug(msg, lock_id, lock_key, poll_interval)
                time.sleep(poll_interval)

        except BaseException:  # Something did go wrong, so decrement the counter.
            self._context.lock_counter = max(0, self._context.lock_counter - 1)
            raise
        return self

    def _release(self) -> None:
        self.client.delete(self.lock_key)
        self._context.success = False

    def release(self, force: bool = False):
        if self.is_locked:
            if force:
                self._context.lock_counter = 0
            else:
                self._context.lock_counter -= 1

            if self._context.lock_counter == 0:
                lock_id, lock_key = id(self), self.lock_key
                logger.debug("Attempting to release lock %s on %s", lock_id, lock_key)
                self._release()
                logger.debug("Lock %s released on %s", lock_id, lock_key)

    def __enter__(self) -> Self:
        return self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
