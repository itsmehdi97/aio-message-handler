import abc
import asyncio
import logging
import functools
from typing import Sequence, Callable

import aio_pika

from .handler import Handler


_log = logging.getLogger(__name__)


class BaseConsumer(metaclass=abc.ABCMeta):
    _handlers: Sequence[Handler]
    _conn: aio_pika.RobustConnection

    def __init__(
        self,
        amqp_url: str,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
    ):
        self.url = amqp_url

        self._queue = queue
        self._exchange = exchange
        self._binding_key = binding_key

        self._handlers = []
        self._stopped = False
        self._conn = None

    def message_handler(
        self,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
        **kwargs
    ):
        def decorator(func: Callable[[aio_pika.IncomingMessage], None]):
            self._handlers.append(
                Handler(
                    queue=queue or self._queue,
                    exchange=exchange or self._exchange,
                    binding_key=binding_key or self._binding_key,
                    cb=func, **kwargs))

            @functools.wraps(func)
            def _decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return _decorator
        return decorator

    @abc.abstractclassmethod
    async def start(self):
        pass

    @abc.abstractclassmethod
    async def stop(self):
        pass


class Consumer(BaseConsumer):
    async def start(self):
        self._conn = await self._connect()
        _log.debug("waiting for messages...")

        [await handler.start(self._conn)
            for handler in self._handlers]

        self._stopped = False

    async def stop(self, timeout=None, nowait: bool = False):
        if self._stopped:
            return

        _log.debug(f"# stopping {len(self._handlers)} handlers...")

        await asyncio.gather(
            *[handler.stop(timeout=timeout, nowait=nowait)
                for handler in self._handlers])
        await self._conn.close()

        self._stopped = True

    async def _connect(self):
        _log.debug(f"# connecting to {self.url}")
        return await aio_pika.connect_robust(self.url)

    def __del__(self):
        _log.debug('consumer deleted.')
