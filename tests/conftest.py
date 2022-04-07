import pytest
from unittest import mock

from aio_message_handler.consumer import Consumer


@pytest.fixture
def create_mock_coro(monkeypatch):
    def _create_mock_patch_coro(to_patch=None):
        m = mock.Mock()

        async def _coro(*args, **kwargs):
            return m(*args, **kwargs)

        if to_patch:
            monkeypatch.setattr(to_patch, _coro)
        return m, _coro

    return _create_mock_patch_coro


@pytest.fixture
def consumer():
    return Consumer(
        amqp_url="url",
        queue="queue",
        exchange="exchange",
        binding_key="key"
    )


@pytest.fixture
def stopped_consumer():
    c = Consumer(
        amqp_url="url",
        queue="queue",
        exchange="exchange",
        binding_key="key"
    )
    c._stopped = True
    return c


@pytest.fixture
def mock_conn():
    mock_connection = mock.Mock()
    return mock_connection
