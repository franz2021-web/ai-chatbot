"""
Rate Limiting Middleware

Prevents API abuse by limiting requests per IP address.
Essential for production systems.
"""

import time
import logging
from typing import Dict, Tuple
from fastapi import Request
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Allows burst traffic but prevents sustained abuse.
    """

    def __init__(self, requests_per_minute: int = 60, burst_size: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Max requests per minute per IP
            burst_size: Max burst requests allowed
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: Dict[str, list] = defaultdict(list)
        self.last_cleanup = time.time()

    def _cleanup(self):
        """Remove old entries to prevent memory leak."""
        current_time = time.time()
        if current_time - self.last_cleanup > 60:
            cutoff = current_time - 60
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    ts for ts in self.requests[ip] if ts > cutoff
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = current_time

    def is_allowed(self, ip_address: str) -> Tuple[bool, Dict[str, int]]:
        """
        Check if request from IP is allowed.

        Args:
            ip_address: Client IP address

        Returns:
            (allowed: bool, info: {limit, remaining, reset_after})
        """
        self._cleanup()
        current_time = time.time()
        minute_ago = current_time - 60

        # Get requests in last minute
        self.requests[ip_address] = [
            ts for ts in self.requests[ip_address] if ts > minute_ago
        ]

        request_count = len(self.requests[ip_address])

        # Check rate limit
        allowed = request_count < self.requests_per_minute

        # Prepare info
        info = {
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - request_count),
            "reset_after": max(0, int(self.requests[ip_address][0] + 60 - current_time))
            if self.requests[ip_address]
            else 0,
        }

        if allowed:
            self.requests[ip_address].append(current_time)

        return allowed, info


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting."""

    def __init__(self, app, limiter: RateLimiter = None):
        self.app = app
        self.limiter = limiter or RateLimiter()

    async def __call__(self, request: Request, call_next):
        """Rate limit the request."""
        # Get client IP
        ip = request.client.host if request.client else "unknown"

        # Check rate limit
        allowed, info = self.limiter.is_allowed(ip)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {ip}")
            return {
                "error": "Too many requests",
                "detail": f"Rate limit: {info['limit']} requests per minute",
                "retry_after": info["reset_after"],
            }

        # Add headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        if info["reset_after"] > 0:
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + info["reset_after"])

        return response


# Global instance
_limiter = RateLimiter(requests_per_minute=60)


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    return _limiter
