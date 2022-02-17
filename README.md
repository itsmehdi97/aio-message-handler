## aio-message-handler
A simple asyncio compatible consumer for handling amqp messages.
### Installation
```
pip install aio-message-handler
```
### Usage example
Simple consumer:
``` python
import asyncio
import signal

from aio_message_handler.consumer import Consumer


async def main():
    consumer = Consumer("amqp://guest:guest@127.0.0.1/")

    async def shutdown(signal, loop):
        print(f"Received exit signal {signal.name}...")
        await consumer.stop()
        loop.stop()

    loop = asyncio.get_event_loop()
    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    @consumer.message_handler(exchange="myexchange", binding_key="key", prefetch_count=5)
    async def handler(msg):
        print('received:', msg.body)
        msg.ack()
    
    await consumer.start()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
    finally:
        loop.close()
```
## Versioning
This software follows [Semantic Versioning](https://semver.org/)
### Development

#### Setting up development environment
Clone the project:
```
git clone https://github.com/itsmehdi97/aio-message-handler.git
cd aio-message-handler
```
Create a virtualenv for [aio-message-handler](https://github.com/itsmehdi97/aio-message-handler):
```
python3 -m venv venv
source venv/bin/activate
```
Install the requirements for [aio-message-handler](https://github.com/itsmehdi97/aio-message-handler):
```
pip install -e '.[develop]'
```