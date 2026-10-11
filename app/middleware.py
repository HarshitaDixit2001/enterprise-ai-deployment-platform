import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.metrics import request_metrics
logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", "").strip()

        # Only accept simple, bounded request IDs from clients.
        if (
            not request_id
            or len(request_id) > 100
            or not all(
                character.isalnum() or character in "-_."
                for character in request_id
            )
        ):
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        started = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )
            request_metrics.record(
                status_code=status_code,
                duration_ms=duration_ms,
            )
            logger.info(
                "request_completed request_id=%s method=%s "
                "path=%s status_code=%s duration_ms=%s",
                request_id,
                request.method,
                request.url.path,
                status_code,
                duration_ms,
            )
