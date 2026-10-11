from threading import Lock


class RequestMetrics:
    """Thread-safe, in-memory HTTP request metrics."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._total_requests = 0
        self._error_requests = 0
        self._total_latency_ms = 0.0
        self._max_latency_ms = 0.0

    def record(
        self,
        status_code: int,
        duration_ms: float,
    ) -> None:
        with self._lock:
            self._total_requests += 1

            if status_code >= 500:
                self._error_requests += 1

            self._total_latency_ms += duration_ms
            self._max_latency_ms = max(
                self._max_latency_ms,
                duration_ms,
            )

    def snapshot(self) -> dict[str, int | float]:
        with self._lock:
            total = self._total_requests

            return {
                "total_requests": total,
                "server_error_requests": self._error_requests,
                "server_error_rate": (
                    round(self._error_requests / total, 4)
                    if total
                    else 0.0
                ),
                "average_latency_ms": (
                    round(self._total_latency_ms / total, 2)
                    if total
                    else 0.0
                ),
                "max_latency_ms": round(
                    self._max_latency_ms,
                    2,
                ),
            }


request_metrics = RequestMetrics()
