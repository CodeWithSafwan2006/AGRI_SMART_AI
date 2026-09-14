"""API middleware for rate limiting, request logging, and response timing.

Provides FastAPI-compatible middleware components for production hardening
of the AgriSmart REST API layer.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("agrismart.api")

# ---------------------------------------------------------------------------
# Request Logger Middleware
# ---------------------------------------------------------------------------

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every inbound API request with method, path, status, and duration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        logger.info(f"→ {method} {path} from {client_ip}")

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            f"← {method} {path} → {response.status_code} ({duration_ms:.1f}ms)"
        )

        # Inject server timing header for observability
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"
        response.headers["X-Served-By"] = "AgriSmart-API"

        return response


# ---------------------------------------------------------------------------
# In-Memory Rate Limiter Middleware
# ---------------------------------------------------------------------------

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding-window rate limiter per client IP.

    Args:
        max_requests: Maximum requests allowed per window.
        window_seconds: Time window in seconds (default 60).
        exempt_paths: List of paths exempt from rate limiting (e.g., health check).
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60, exempt_paths: list[str] | None = None):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.exempt_paths = set(exempt_paths or ["/api/health", "/", "/static"])
        self._request_log: dict[str, list[float]] = defaultdict(list)

    def _cleanup_window(self, client_ip: str, now: float) -> None:
        """Remove timestamps outside the current sliding window."""
        cutoff = now - self.window_seconds
        self._request_log[client_ip] = [
            ts for ts in self._request_log[client_ip] if ts > cutoff
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Skip rate limiting for exempt paths
        if any(path.startswith(ep) for ep in self.exempt_paths):
            return await call_next(request)

        client_ip = request.client.host if request.client else "0.0.0.0"
        now = time.time()

        self._cleanup_window(client_ip, now)

        if len(self._request_log[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
            return Response(
                content='{"detail": "Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        self._request_log[client_ip].append(now)
        remaining = self.max_requests - len(self._request_log[client_ip])

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response


# ---------------------------------------------------------------------------
# CORS Security Headers Middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject standard security headers into every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


# ---------------------------------------------------------------------------
# Setup helper
# ---------------------------------------------------------------------------

def configure_logging(level: str = "INFO") -> None:
    """Configure structured API logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
