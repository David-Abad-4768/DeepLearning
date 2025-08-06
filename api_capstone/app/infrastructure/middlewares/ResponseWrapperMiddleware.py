import json
from typing import AsyncIterable, cast

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

EXCLUDE_PATHS = {
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
}


class ResponseWrapperMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDE_PATHS:
            return await call_next(request)

        original: Response = await call_next(request)

        if not original.headers.get("content-type", "").startswith("application/json"):
            return original

        if isinstance(original, StreamingResponse) or not hasattr(original, "body"):
            chunks = [
                c async for c in cast(AsyncIterable[bytes], original.body_iterator)
            ]
            body_bytes = b"".join(chunks)
        else:
            body_bytes = bytes(original.body)  # type: ignore[attr-defined]

        try:
            payload = json.loads(body_bytes.decode())
        except Exception:
            payload = body_bytes.decode(errors="replace")

        wrapped = {
            "error": original.status_code >= 400,
            "data": payload,
        }

        response = JSONResponse(content=wrapped, status_code=original.status_code)

        for k, v in original.headers.items():
            if k.lower() not in {"content-type", "content-length"}:
                response.headers[k] = v

        return response
