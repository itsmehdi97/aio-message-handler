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
