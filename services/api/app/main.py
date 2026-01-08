from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .models import ClickstreamEvent, IngestResponse
from .clickhouse import ClickHouseClient

CLICKHOUSE_URL = "http://clickhouse:8123"

# Инициализация приложения
app = FastAPI(
    title="Clickstream Ingest API",
    version="0.1.0",
)

ch = ClickHouseClient(CLICKHOUSE_URL)

# Проверка доступности сервиса
@app.get("/health")
async def health():
    return {"status": "ok"}

# Прием и сохранение clickstream-событий
@app.post("/events", response_model=IngestResponse)
async def ingest_events(events: list[ClickstreamEvent]):
    payload = [e.model_dump(mode="json") for e in events]
    inserted = await ch.insert_raw_events(payload, source="http")
    return IngestResponse(inserted=inserted)