import abc
import asyncio
import logging
import functools
from typing import Sequence, Callable

import aio_pika

from .handler import Handler
from . import exceptions


logger = logging.getLogger(__name__)


class BaseConsumer(metaclass=abc.ABCMeta):
    _handlers: Sequence[Callable]
    _tasks: Sequence[asyncio.Task]
    _conn: aio_pika.RobustConnection

    def __init__(self, rmq_url: str):
        self.url = rmq_url

        self._handlers = []
        self._closed = False
        self._conn = None

    def message_handler(self, *, 
        queue: str,
        exchange: str = None,
        binding_key: str = None
    ):
        def decorator(func: Callable[[aio_pika.IncomingMessage], None]):
            handler = Handler(
                queue=queue,
                exchange=exchange,
                binding_key=binding_key,
                cb=func)
            self._handlers.append(handler)

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
        await self._connect()
        self.__class__._tasks = [
            await self._run_in_bg(handler) 
            for handler in self._handlers]
        
        await asyncio.gather(*self._tasks)
    
    async def stop(self):
        if self._closed:
            return

        return await self._conn.close()
    
    async def _connect(self):
        self._conn = await aio_pika.connect_robust(self.url)


    async def _run_in_bg(self, handler: Handler) -> asyncio.Task:
        conn = self._conn
        async def job():
            async with conn.channel() as channel:
                await channel.set_qos(prefetch_count=handler.prefetch_count)
                q = None
                exc = None
                if handler.exchange:
                    try:
                        exc = await channel.get_exchange(handler.exchange)
                    except aio_pika.exceptions.ChannelNotFoundEntity as _:
                        raise exceptions.ExchangeNotFound

                    q = await channel.declare_queue(
                        name=handler.queue,
                        durable=False,
                        exclusive=False,
                        passive=False,
                        auto_delete=False) 

                    await q.bind(exc, routing_key=handler.binding_key)
                else:
                    q = await channel.get_queue(handler.queue)

                logger.info(f"{repr(handler)} started consuming...")
                while True:
                    await q.consume(handler.cb)
            
        return asyncio.create_task(job())