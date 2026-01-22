import pytest
import pika
from unittest.mock import patch, MagicMock

from services.consumer.consumer import wait_for_rabbit


def test_wait_for_rabbit_success():
    with patch("pika.BlockingConnection") as mock_conn:
        mock_conn.return_value = MagicMock()
        conn = wait_for_rabbit("rabbitmq", retries=1)
        assert conn is not None


def test_wait_for_rabbit_retries_and_fails():
    with patch("pika.BlockingConnection", side_effect=pika.exceptions.AMQPConnectionError):
        with pytest.raises(RuntimeError):
            wait_for_rabbit("rabbitmq", retries=2, delay=0)