import json
import time
from unittest.mock import MagicMock

def test_consumer_callback_ack_and_flush():
    batch = []
    last_flush = time.time() - 10

    client = MagicMock()
    response = MagicMock()
    response.raise_for_status.return_value = None
    client.post.return_value = response

    channel = MagicMock()
    method = MagicMock()
    method.delivery_tag = "tag"

    def flush():
        client.post("http://api/events", json=batch)
        batch.clear()

    def callback(channel, method, properties, body):
        nonlocal last_flush
        event = json.loads(body.decode("utf-8"))
        batch.append(event)
        flush()
        channel.basic_ack(delivery_tag=method.delivery_tag)

    callback(
        channel,
        method,
        None,
        json.dumps({"event": "click"}).encode("utf-8"),
    )

    channel.basic_ack.assert_called_once_with(delivery_tag="tag")
    client.post.assert_called_once()