import pytest
from unittest import mock

from aio_message_handler.consumer import Consumer


@pytest.fixture
def mock_handler():
    return mock.Mock(name="Handler")


@pytest.mark.asyncio
async def test_consumer_connect(create_mock_coro, consumer: Consumer):
    mock_connect, _ = create_mock_coro(
        to_patch="aio_message_handler.consumer.aio_pika.connect_robust")
    mock_connect.return_value = "connection"

    result = await consumer._connect()
    assert result == mock_connect.return_value

    mock_connect.assert_called_once_with(consumer.url)


@pytest.mark.asyncio
async def test_consumer_start(create_mock_coro, consumer: Consumer, mock_handler):
    mock_connect, _ = create_mock_coro(
        to_patch="aio_message_handler.consumer.Consumer._connect")
    mock_connect.return_value = "connection"

    mock_start, coro = create_mock_coro()
    mock_handler.start = coro

    consumer._handlers = [mock_handler]

    await consumer.start()

    assert consumer._conn == mock_connect.return_value
    assert mock_start.call_count == 1
    assert not consumer._stopped


@pytest.mark.asyncio
async def test_running_consumer_stop(
    mock_conn, create_mock_coro, consumer: Consumer, mock_handler
):
    mock_gather, _ = create_mock_coro(
        to_patch="aio_message_handler.consumer.asyncio.gather")

    mock_stop = mock.Mock()
    mock_stop.return_value = 'coroutine'
    mock_handler.stop = mock_stop
    consumer._handlers = [mock_handler]

    mock_close, coro = create_mock_coro()
    mock_conn.close = coro
    consumer._conn = mock_conn

    await consumer.stop(timeout=5, nowait=True)

    assert consumer._stopped
    assert mock_close.call_count == 1
    mock_stop.assert_called_once_with(timeout=5, nowait=True)
    mock_gather.assert_called_once_with(mock_stop.return_value)


@pytest.mark.asyncio
async def test_stopped_consumer_stop(
    mock_conn, create_mock_coro, stopped_consumer: Consumer, mock_handler
):
    assert stopped_consumer._stopped

    mock_stop = mock.Mock()
    mock_stop.return_value = 'coroutine'
    mock_handler.stop = mock_stop
    stopped_consumer._handlers = [mock_handler]

    mock_close, coro = create_mock_coro()
    mock_conn.close = coro
    stopped_consumer._conn = mock_conn

    await stopped_consumer.stop(timeout=5, nowait=True)

    assert stopped_consumer._stopped
    assert mock_close.call_count == 0
    assert mock_stop.call_count == 0


def test_add_handler(
    monkeypatch,
    consumer: Consumer,
    mock_handler
):
    monkeypatch.setattr("aio_message_handler.consumer.Handler", mock_handler)

    add_handler = consumer.message_handler(
        queue="queue",
        exchange="exchange",
        binding_key="key",
        prefetch_count=1
    )

    def handler_functoin(msg):
        pass
    add_handler(handler_functoin)

    assert len(consumer._handlers) == 1
    mock_handler.assert_called_once_with(
        handler_functoin,
        queue="queue",
        exchange="exchange",
        binding_key="key",
        prefetch_count=1
    )


def test_add_handler_without_confs(
    monkeypatch,
    consumer: Consumer,
    mock_handler
):
    monkeypatch.setattr("aio_message_handler.consumer.Handler", mock_handler)

    add_handler = consumer.message_handler()

    def handler_functoin(msg):
        pass

    add_handler(handler_functoin)

    mock_handler.assert_called_once_with(
        handler_functoin,
        queue=consumer._queue,
        exchange=consumer._exchange,
        binding_key=consumer._binding_key,
        prefetch_count=1
    )
    assert len(consumer._handlers) == 1
