import pytest
from prometheus_client import CollectorRegistry

from services.api.app import metrics


def test_ingest_events_counter_exists():
    # Counter должен существовать и иметь корректное имя
    counter = metrics.INGEST_EVENTS_TOTAL
    assert counter is not None
    assert counter._name == "clickstream_ingest_events"

def test_ingest_events_counter_has_source_label():
    # Counter должен принимать label source
    counter = metrics.INGEST_EVENTS_TOTAL
    child = counter.labels(source="api")
    assert child is not None


def test_ingest_events_counter_increment():
    # Counter должен инкрементиться
    counter = metrics.INGEST_EVENTS_TOTAL
    child = counter.labels(source="test")

    # Получаем текущее значение
    before = child._value.get()
    child.inc()
    after = child._value.get()

    assert after == before + 1


def test_ingest_latency_histogram_exists():
    # Histogram должен существовать и иметь корректное имя
    histogram = metrics.INGEST_LATENCY
    assert histogram is not None
    assert histogram._name == "clickstream_ingest_latency_seconds"


def test_ingest_latency_histogram_observe():
    # Histogram должен принимать observe
    histogram = metrics.INGEST_LATENCY

    histogram.observe(0.123)
    histogram.observe(1.456)