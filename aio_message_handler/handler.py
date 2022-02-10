import asyncio
import uuid
import logging
from typing import Callable

from aio_pika import IncomingMessage
import aio_pika


_log = logging.getLogger(__name__)


class Handler:
    def __init__(self,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
        cb: Callable[[IncomingMessage], None] = None,
        prefetch_count: int = 1
    ):
        self._ready = False
        self._name = cb.__name__

        self._queue = queue or uuid.uuid4().hex
        self._exchange = exchange
        self._binding_key = binding_key or exchange
        self.prefetch_count = prefetch_count
        self.cb = cb

        self.queue = None
        self.exchange = None

    @property
    def ready(self):
        return self._ready

    async def setup(self, channel: aio_pika.Channel) -> aio_pika.Queue:
        # TODO: handle signature conflicts.
        _log.debug(f"# setting up handler {self._name}")

        queue = await channel.declare_queue(self._queue)
        if self._exchange:
            exchange = await channel.declare_exchange(self._exchange)
            await queue.bind(exchange, routing_key=self._binding_key)

        await channel.set_qos(prefetch_count=self.prefetch_count)

        self._ready = True
        return queue

    async def start(self, conn: aio_pika.Connection) -> asyncio.Task:
        channel = await conn.channel()
        queue = await self.setup(channel)
        return asyncio.create_task(queue.consume(self.cb))

    async def stop(self):
        pass

    def __repr__(self):
        return f"{self.__name__} -> queue:{self._queue} bindingkey:{self.binding_key} exchange:{self._exchange}"
