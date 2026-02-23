
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get('X-Request-Id') or str(uuid.uuid4())
        request.state.request_id = rid
        start = time.time()
        resp = await call_next(request)
        resp.headers['X-Request-Id'] = rid
        resp.headers['X-Response-Time-ms'] = str(int((time.time()-start)*1000))
        return resp
