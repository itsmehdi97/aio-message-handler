import asyncio
from abc import ABCMeta, abstractclassmethod
from logging import getLogger
from typing import Sequence, Callable

import aio_pika

from .handler import Handler
from . import exceptions


logger = getLogger(__name__)


class BaseConsumer(metaclass=ABCMeta):
    handlers: Sequence[Callable] = []
    _tasks: Sequence[asyncio.Task]
    _conn: aio_pika.RobustConnection

    def __init__(self, rmq_url: str):
        self.url = rmq_url

    @classmethod
    def add_handler(cls, handler: Handler):
        cls.handlers.append(handler)
        logger.info(f'registered handler: {repr(handler)}')

    @abstractclassmethod
    async def start_consuming(self):
        pass

    
class Consumer(BaseConsumer):
    async def connect(self):
        self._conn = await aio_pika.connect_robust(self.url)
        
    async def start_consuming(self):
        await self.connect()
        self.__class__._tasks = [
            await self._run_in_bg(handler) 
            for handler in self.handlers]
        
        await asyncio.wait(
            self._tasks, return_when=asyncio.ALL_COMPLETED)


    async def _run_in_bg(self, handler: Handler) -> asyncio.Task:
        conn = self._conn
        async def job():
            async with conn.channel() as channel:
                await channel.set_qos(prefetch_count=handler.prefetch_count)
                try:
                    exc = await channel.get_exchange(handler.exchange, ensure=True)
                except aio_pika.exceptions.ChannelNotFoundEntity as _:
                    raise exceptions.ExchangeNotFound

                q = await channel.declare_queue(
                    name=handler.queue,
                    durable=False,
                    exclusive=False,
                    passive=False,
                    auto_delete=False)

                await q.bind(exc, routing_key=handler.binding_key)
                logger.info(f"{repr(handler)} started consuming...")
                while True:
                    await q.consume(handler.cb)
            
        return asyncio.create_task(job())