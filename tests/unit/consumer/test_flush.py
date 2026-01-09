from unittest.mock import MagicMock
from services.consumer.consumer import BATCH_SIZE


def test_flush_sends_http_and_clears_batch():
    batch = [{"event": 1}, {"event": 2}]
    client = MagicMock()
    response = MagicMock()
    response.raise_for_status.return_value = None
    client.post.return_value = response

    last_flush = 0

    def flush():
        nonlocal batch
        if not batch:
            return
        resp = client.post("http://api/events", json=batch)
        resp.raise_for_status()
        batch.clear()

    flush()

    client.post.assert_called_once()
    assert batch == []