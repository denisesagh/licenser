import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from restapi.license import router as license_router

ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS')
ALLOWED_HEADERS = os.getenv('ALLOWED_HEADERS').split(",")
MODE = os.getenv('MODE')
AUTH_TOKENS = os.getenv('AUTH_TOKENS').split(",")


app = FastAPI(debug=False)

app.include_router(license_router, prefix="/api/v1/license", tags=["license"])

@app.exception_handler(HTTPException)
async def http_exception_handler_custom(request: Request, exc: HTTPException):
    print(f"HTTPException: {exc.detail}")
    return await http_exception_handler(request, exc)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "DELETE"],
    allow_headers=ALLOWED_HEADERS,
    max_age=3600,
    expose_headers=["Content-Length"],
    allow_origin_regex=None
)

app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_ORIGINS,
    )

app.add_middleware(
        GZipMiddleware,
        minimum_size=1000
    )
app.add_middleware(
    ServerErrorMiddleware,
)

@app.middleware("http")
async def check_bearer_token(request: Request, call_next):

    if (request.url.path.startswith("/api/v1/license/validate")
            and request.method == "GET"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing Authorization header"}
        )
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid Authorization header format"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token not in AUTH_TOKENS:
        print(AUTH_TOKENS)
        print(token)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    response = await call_next(request)
    return response


if __name__ == '__main__':
    print("Running in mode:", MODE)
    if MODE == "DEV":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000)