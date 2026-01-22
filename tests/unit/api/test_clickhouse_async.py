import pytest
from unittest.mock import AsyncMock, patch
from services.api.app.clickhouse import ClickHouseClient


@pytest.mark.asyncio
@patch("services.api.app.clickhouse.httpx.AsyncClient")
async def test_insert_raw_events(mock_client):
    mock_response = AsyncMock()
    mock_response.raise_for_status.return_value = None

    mock_instance = AsyncMock()
    mock_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_instance

    events = [
        {
            "type": "click",
            "created_at": "2026-01-10T10:00:00.123Z",
            "session_id": "s1",
            "user_id": 42,
            "url": "/home",
            "payload": {"x": 10},
        },
        {
            "type": "view",
            "created_at": "2026-01-10T10:01:00.456Z",
            "session_id": "s2",
            "user_id": 43,
            "url": "/about",
        },
    ]

    client = ClickHouseClient("http://clickhouse:8123")

    inserted = await client.insert_raw_events(events, source="test")

    assert inserted == 2

    # Проверяем, что HTTP POST был вызван
    mock_instance.post.assert_called_once()