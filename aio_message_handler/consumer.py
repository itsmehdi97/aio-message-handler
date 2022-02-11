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

    def __init__(self, amqp_url: str,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
    ):
        self.url = amqp_url

        self._queue = queue
        self._exchange = exchange
        self._binding_key = binding_key

        self._handlers = []
        self._closed = False
        self._conn = None

    def message_handler(self,
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
        conn = await self._connect()
        _log.debug(f"waiting for messages...")
        
        [ await handler.start(conn)
        for handler in self._handlers]

    
    async def stop(self):
        if self._closed:
            return

        _log.debug(f"# stopping {len(self._handlers)} handlers...")
        for handler in self._handlers:
            await handler.stop()
    
    async def _connect(self):
        _log.debug(f"# connecting to {self.url}")
        return await aio_pika.connect_robust(self.url)