import services.api.app.metrics_http as metrics


def test_http_requests_counter_exists():
    counter = metrics.HTTP_REQUESTS_TOTAL
    assert counter is not None
    assert counter._name == "http_requests"


def test_http_requests_counter_labels():
    counter = metrics.HTTP_REQUESTS_TOTAL
    assert set(counter._labelnames) == {"method", "path", "status"}


def test_http_latency_histogram_exists():
    histogram = metrics.HTTP_REQUEST_LATENCY
    assert histogram is not None
    assert histogram._name == "http_request_latency_seconds"


def test_http_latency_histogram_labels():
    histogram = metrics.HTTP_REQUEST_LATENCY
    assert set(histogram._labelnames) == {"path"}