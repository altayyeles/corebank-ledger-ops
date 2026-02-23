
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.core.db import SessionLocal
from src.core.utils import uid
from src.audit.models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        if request.method in ('POST','PUT','PATCH','DELETE'):
            try:
                actor = getattr(request.state, 'user_id', None)
                with SessionLocal() as db:
                    db.add(AuditLog(
                        id=uid(),
                        actor_user_id=actor,
                        action=f"{request.method} {request.url.path}",
                        entity_type=request.url.path.split('/')[1] if request.url.path else 'unknown',
                        entity_id=getattr(request.state, 'request_id', 'n/a'),
                        after_json={'status_code': resp.status_code},
                    ))
                    db.commit()
            except Exception:
                pass
        return resp
