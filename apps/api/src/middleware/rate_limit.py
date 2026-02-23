
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rps: float = 20.0):
        super().__init__(app)
        self.rps = rps
        self.buckets = {}

    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else 'unknown'
        now = time.time()
        tokens, last = self.buckets.get(key, (self.rps, now))
        tokens = min(self.rps, tokens + (now-last)*self.rps)
        if tokens < 1.0:
            return JSONResponse({'detail':'Rate limit exceeded'}, status_code=429)
        self.buckets[key] = (tokens-1.0, now)
        return await call_next(request)
