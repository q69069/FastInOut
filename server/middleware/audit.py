from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from database import SessionLocal
from models.http_audit_log import HttpAuditLog
from utils.auth import decode_access_token
import logging

logger = logging.getLogger(__name__)

SKIP_PATHS = {"/api/health", "/api/auth/login", "/docs", "/openapi.json", "/redoc"}
SKIP_METHODS = {"GET", "OPTIONS", "HEAD"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.method in SKIP_METHODS:
            return response
        if request.url.path in SKIP_PATHS:
            return response

        user_id = None
        try:
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                payload = decode_access_token(token)
                if payload:
                    user_id = payload.get("sub")
        except Exception:
            pass

        if not user_id:
            return response

        path_parts = request.url.path.strip("/").split("/")
        entity_type = path_parts[1] if len(path_parts) > 1 else "unknown"

        db = SessionLocal()
        try:
            log = HttpAuditLog(
                user_id=int(user_id),
                method=request.method,
                path=request.url.path,
                entity_type=entity_type,
                ip_address=request.client.host if request.client else "",
                user_agent=request.headers.get("user-agent", "")[:200],
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Audit middleware error: {e}")
            db.rollback()
        finally:
            db.close()

        return response
