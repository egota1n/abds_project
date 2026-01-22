import time
from fastapi import Request
from prometheus_client import Counter, Histogram

# Количество HTTP-запросов
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

# Задержка HTTP-запросов
HTTP_REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["path"]
)

# Middleware для сбора HTTP метрик
async def prometheus_http_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    HTTP_REQUESTS_TOTAL.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    ).inc()

    HTTP_REQUEST_LATENCY.labels(
        path=request.url.path
    ).observe(duration)

    return response