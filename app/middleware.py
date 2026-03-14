import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

REQUIRED_VARS = ["OPENWEATHER_API_KEY", "GITHUB_TOKEN", "GIST_ID"]


class ConfigMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
        if missing:
            return JSONResponse(
                status_code=500,
                content={"detail": f"Configuracao ausente: {', '.join(missing)}"},
            )
        return await call_next(request)
