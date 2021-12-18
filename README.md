## aio-message-handler
A simple asyncio compatible consumer for handling amqp messages.
### Installation
```
pip install aio-message-handler
```
### Usage example
Simple consmer:
``` python
import asyncio

from aio_message_handler.consumer import Consumer


async def main():
    consumer = Consumer("amqp://guest:guest@127.0.0.1/")

    @consumer.message_handler(exchange="myexchange", binding_key="key")
    async def handler(msg):
        print('received:', msg.body)
        msg.ack()
    
    await consumer.start()

asyncio.run(main())
```
### Versioning
___
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
pip install -e `.[develop]`
```