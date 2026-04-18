from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import get_settings
from app.models.models import ActionLog
import time
import re

settings = get_settings()

# ─────────────────────────────────────────────────
#  RATE LIMITER (slowapi)
# ─────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─────────────────────────────────────────────────
#  MIDDLEWARE: CABECERAS DE SEGURIDAD
# ─────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"]    = "nosniff"
        response.headers["X-Frame-Options"]           = "DENY"
        response.headers["X-XSS-Protection"]          = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"]            = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"]              = "no-store"
        # Ocultar que usamos FastAPI
        response.headers["Server"]                    = "ReactorGuard"
        return response


# ─────────────────────────────────────────────────
#  MIDDLEWARE: BLOQUEO DE INPUTS MALICIOSOS
# ─────────────────────────────────────────────────
INJECTION_PATTERNS = re.compile(
    r"(\$where|\$ne|\$gt|\$lt|<script|javascript:|union\s+select|drop\s+table)",
    re.IGNORECASE,
)

class InputSanitizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Revisar query params
        raw_query = str(request.url.query)
        if INJECTION_PATTERNS.search(raw_query):
            return JSONResponse(
                status_code=400,
                content={"detail": "Input inválido detectado"},
            )
        # Revisar body si es JSON
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body = await request.body()
                if INJECTION_PATTERNS.search(body.decode("utf-8", errors="ignore")):
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Input inválido detectado"},
                    )
            except Exception:
                pass
        return await call_next(request)


# ─────────────────────────────────────────────────
#  MIDDLEWARE: AUDITORÍA (log de cada request)
# ─────────────────────────────────────────────────
class AuditLogMiddleware(BaseHTTPMiddleware):
    SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/health"}

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start   = time.time()
        response = await call_next(request)
        duration = round(time.time() - start, 4)

        # Solo loguear endpoints de negocio
        if request.url.path.startswith("/api") or request.url.path.startswith("/auth"):
            try:
                user_id    = getattr(request.state, "user_id", "anonymous")
                user_email = getattr(request.state, "user_email", "anonymous")
                await ActionLog(
                    user_id    = user_id,
                    user_email = user_email,
                    action     = f"{request.method} {request.url.path}",
                    endpoint   = request.url.path,
                    ip_address = get_remote_address(request),
                    success    = response.status_code < 400,
                    details    = f"status={response.status_code} duration={duration}s",
                ).insert()
            except Exception:
                pass  # No romper el flujo si falla el log

        return response


# ─────────────────────────────────────────────────
#  FUNCIÓN: Registrar todos los middlewares
# ─────────────────────────────────────────────────
def register_middlewares(app: FastAPI):
    # 1. CORS estricto
    app.add_middleware(
        CORSMiddleware,
        allow_origins     = settings.origins_list,
        allow_credentials = True,
        allow_methods     = ["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers     = ["Authorization", "Content-Type"],
    )
    # 2. Cabeceras de seguridad
    app.add_middleware(SecurityHeadersMiddleware)
    # 3. Sanitización de inputs
    app.add_middleware(InputSanitizationMiddleware)
    # 4. Auditoría
    app.add_middleware(AuditLogMiddleware)

    # 5. Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
