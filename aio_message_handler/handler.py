from logging import getLogger
from typing import Callable

from aio_pika import IncomingMessage


logger = getLogger(__name__)


class Handler:
    def __init__(self, *,
        queue: str,
        cb: Callable[[IncomingMessage], None],
        exchange: str = None,
        binding_key: str = None,
        prefetch_count: int = 1
    ):
        self.queue = queue
        self.exchange = exchange
        self.binding_key = binding_key
        self.prefetch_count = prefetch_count
        self.cb = cb

    def __repr__(self):
        return f"{self.cb.__name__} -> queue:{self.queue} bindingkey:{self.binding_key} exchange:{self.exchange}"
