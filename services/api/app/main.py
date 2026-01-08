from __future__ import annotations
import time
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .models import ClickstreamEvent, IngestResponse
from .clickhouse import ClickHouseClient
from .metrics import INGEST_EVENTS_TOTAL, INGEST_LATENCY
from .metrics_http import prometheus_http_middleware

CLICKHOUSE_URL = "http://clickhouse:8123"

# Инициализация приложения
app = FastAPI(
    title="Clickstream Ingest API",
    version="0.1.0",
)
ch = ClickHouseClient(CLICKHOUSE_URL)

app.middleware("http")(prometheus_http_middleware)

# Проверка доступности сервиса
@app.get("/health")
async def health():
    return {"status": "ok"}

# Ключевые бизнес-метрики
@app.get("/metrics")
async def metrics():
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

# Прием и сохранение clickstream-событий
@app.post("/events", response_model=IngestResponse)
async def ingest_events(events: list[ClickstreamEvent]):
    start = time.time()
    payload = [e.model_dump(mode="json") for e in events]
    inserted = await ch.insert_raw_events(payload, source="http")
    INGEST_EVENTS_TOTAL.labels(source="http").inc(inserted)
    INGEST_LATENCY.observe(time.time() - start)
    return IngestResponse(inserted=inserted)