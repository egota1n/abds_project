from fastapi import FastAPI
from fastapi.testclient import TestClient

from services.api.app.metrics_http import (
    prometheus_http_middleware,
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_LATENCY,
)


def create_test_app():
    app = FastAPI()
    app.middleware("http")(prometheus_http_middleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


def test_prometheus_http_middleware_collects_metrics():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test")
    assert response.status_code == 200

    # Проверяем, что счётчик увеличился
    samples = list(HTTP_REQUESTS_TOTAL.collect())[0].samples
    assert any(
        s.labels["method"] == "GET"
        and s.labels["path"] == "/test"
        and s.labels["status"] == "200"
        for s in samples
    )

    # Проверяем, что latency записалась
    latency_samples = list(HTTP_REQUEST_LATENCY.collect())[0].samples
    assert any(
        s.labels["path"] == "/test"
        for s in latency_samples
    )