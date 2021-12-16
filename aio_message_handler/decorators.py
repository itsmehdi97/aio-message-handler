import functools
from typing import Callable

from aio_pika import IncomingMessage

from .consumer import Consumer
from .handler import Handler


def message_handler(*, 
        queue: str,
        exchange: str = None,
        binding_key: str = None
    ):
        def decorator(func: Callable[[IncomingMessage], None]):
            handler = Handler(
                queue=queue,
                exchange=exchange,
                binding_key=binding_key,
                cb=func)
            Consumer.add_handler(handler)

            @functools.wraps(func)
            def _decorator(*args, **kwargs):
                return func(*args, **kwargs)
            return _decorator
        return decorator