import pytest
from unittest import mock

from aio_message_handler.handler import Handler


@pytest.fixture
def handler():
    def cb():
        pass

    return Handler(
        cb,
        queue="queue",
        exchange="exchange",
        binding_key="key",
        prefetch_count=1
    )


@pytest.fixture
def running_handler(monkeypatch, handler: Handler):
    handler._ctag = "ctag"
    handler.queue = mock.Mock(name="queue")
    return handler


@pytest.mark.asyncio
async def test_handler_start(create_mock_coro, mock_conn, handler: Handler):
    mock_setup, _ = create_mock_coro(
        to_patch="aio_message_handler.handler.Handler.setup")
    mock_queue = mock.Mock(name='queue')
    mock_setup.return_value = mock_queue
    mock_consume, mock_queue.consume = create_mock_coro()
    mock_consume.return_value = 'ctag'

    mock_channel, mock_conn.channel = create_mock_coro()
    mock_channel.return_value = 'channel'

    await handler.start(mock_conn)

    assert mock_channel.call_count == 1
    assert mock_setup.call_count == 1
    assert handler._ctag == mock_consume.return_value
    mock_consume.assert_called_once_with(handler.cb)


@pytest.mark.asyncio
async def test_handler_stop(
    create_mock_coro,
    running_handler: Handler
):
    mock_cancel, coro = create_mock_coro()
    running_handler.queue.cancel = coro

    await running_handler.stop(timeout='timeout', nowait='nowait')

    mock_cancel.assert_called_once_with(
        running_handler._ctag, timeout='timeout', nowait='nowait')


@pytest.mark.asyncio
async def test_handler_with_exchange_setup(
    create_mock_coro,
    handler: Handler
):
    mock_channel = mock.Mock()
    mock_declare_q, mock_channel.declare_queue = create_mock_coro()
    mock_declare_exc, mock_channel.declare_exchange = create_mock_coro()
    mock_set_qos, mock_channel.set_qos = create_mock_coro()

    mock_declare_exc.return_value = 'exchange'
    mock_queue = mock.Mock(name="queue")
    mock_declare_q.return_value = mock_queue
    mock_bind, mock_queue.bind = create_mock_coro()

    result = await handler.setup(mock_channel)

    assert result == mock_queue
    assert handler._ready is True
    mock_declare_exc.assert_called_once_with(handler._exchange)
    mock_declare_q.assert_called_once_with(handler._queue)
    mock_bind.assert_called_once_with(
        mock_declare_exc.return_value, routing_key=handler._binding_key)
    mock_set_qos.assert_called_once_with(prefetch_count=handler.prefetch_count)


@pytest.mark.asyncio
async def test_handler_without_exchange_setup(
    create_mock_coro,
    handler: Handler
):
    handler._exchange = None

    mock_channel = mock.Mock()
    mock_declare_q, mock_channel.declare_queue = create_mock_coro()
    mock_declare_exc, mock_channel.declare_exchange = create_mock_coro()
    mock_set_qos, mock_channel.set_qos = create_mock_coro()

    mock_declare_exc.return_value = 'exchange'
    mock_queue = mock.Mock(name="queue")
    mock_declare_q.return_value = mock_queue
    mock_bind, mock_queue.bind = create_mock_coro()

    result = await handler.setup(mock_channel)

    assert result == mock_queue
    assert mock_declare_exc.call_count == 0
    assert mock_bind.call_count == 0
    assert handler._ready is True
    mock_declare_q.assert_called_once_with(handler._queue)
    mock_set_qos.assert_called_once_with(prefetch_count=handler.prefetch_count)


def test_repr(handler: Handler):
    names = [
        handler._name,
        handler._queue,
        handler._exchange,
        handler._binding_key]
    result = repr(handler)
    for name in names:
        assert name in result
