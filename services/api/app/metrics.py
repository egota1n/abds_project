from prometheus_client import Counter, Histogram

# Количество успешно принятых событий
INGEST_EVENTS_TOTAL = Counter(
    "clickstream_ingest_events_total",
    "Total ingested clickstream events",
    ["source"],
)

# Время обработки батча событий
INGEST_LATENCY = Histogram(
    "clickstream_ingest_latency_seconds",
    "Latency of ingest handler",
)