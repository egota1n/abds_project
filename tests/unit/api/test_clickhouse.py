import pytest
from services.api.app.clickhouse import ch_datetime, ClickHouseClient


def test_ch_datetime_iso_format():
    dt = "2026-01-10T12:34:56.789Z"
    assert ch_datetime(dt) == "2026-01-10 12:34:56"


def test_ch_datetime_without_ms():
    dt = "2026-01-10T12:34:56Z"
    assert ch_datetime(dt) == "2026-01-10 12:34:56"


def test_clickhouse_client_init():
    client = ClickHouseClient(
        base_url="http://localhost:8123/",
        database="raw",
        table="events",
    )

    assert client.base_url == "http://localhost:8123"
    assert client.database == "raw"
    assert client.table == "events"