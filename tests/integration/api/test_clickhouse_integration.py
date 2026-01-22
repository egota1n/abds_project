import pytest
from unittest.mock import AsyncMock, patch
from services.api.app.clickhouse import ClickHouseClient


@pytest.mark.asyncio
@patch("services.api.app.clickhouse.httpx.AsyncClient")
async def test_clickhouse_http_contract(mock_client):
    mock_response = AsyncMock()
    mock_response.raise_for_status.return_value = None

    mock_instance = AsyncMock()
    mock_instance.post.return_value = mock_response
    mock_client.return_value.__aenter__.return_value = mock_instance

    client = ClickHouseClient(
        base_url="http://clickhouse:8123",
        database="raw",
        table="events",
    )

    events = [{
        "type": "view",
        "created_at": "2026-01-10T12:00:00Z",
        "session_id": "abc",
        "user_id": 1,
        "url": "/",
    }]

    await client.insert_raw_events(events, source="integration-test")

    args, kwargs = mock_instance.post.call_args

    assert kwargs["params"]["database"] == "raw"
    assert "INSERT INTO events" in kwargs["params"]["query"]