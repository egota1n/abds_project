import json
import time
from unittest.mock import MagicMock

from services.consumer.consumer import BATCH_SIZE


def test_batch_flush_by_size():
    batch = []
    client = MagicMock()
    response = MagicMock()
    response.raise_for_status.return_value = None
    client.post.return_value = response

    def flush():
        client.post("http://api/events", json=batch)
        batch.clear()

    for i in range(BATCH_SIZE):
        batch.append({"id": i})

    flush()

    client.post.assert_called_once()
    assert batch == []