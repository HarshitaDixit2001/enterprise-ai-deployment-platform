from app.core.metrics import RequestMetrics


def test_metrics_start_at_zero():
    metrics = RequestMetrics()

    result = metrics.snapshot()

    assert result["total_requests"] == 0
    assert result["server_error_requests"] == 0
    assert result["server_error_rate"] == 0.0
    assert result["average_latency_ms"] == 0.0


def test_metrics_track_requests_and_latency():
    metrics = RequestMetrics()

    metrics.record(status_code=200, duration_ms=100)
    metrics.record(status_code=500, duration_ms=300)
    metrics.record(status_code=404, duration_ms=200)

    result = metrics.snapshot()

    assert result["total_requests"] == 3
    assert result["server_error_requests"] == 1
    assert result["server_error_rate"] == 0.3333
    assert result["average_latency_ms"] == 200.0
    assert result["max_latency_ms"] == 300.0


def test_metrics_count_only_server_errors_as_errors():
    metrics = RequestMetrics()

    metrics.record(status_code=200, duration_ms=10)
    metrics.record(status_code=404, duration_ms=20)
    metrics.record(status_code=503, duration_ms=30)

    result = metrics.snapshot()

    assert result["total_requests"] == 3
    assert result["server_error_requests"] == 1
