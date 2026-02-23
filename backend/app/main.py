from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse

from app.config import config
from app.routers.v1 import v1_router
from app.schemas.system import AppBaseResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine
    from app.redis import redis_client

    yield

    redis_client.close()
    engine.dispose()

app = FastAPI(title=config.APP_NAME, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    body = AppBaseResponse[None](
        status=exc.status_code,
        message=detail.get("message", "error"),
        errors=detail.get("errors", None),
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    body = AppBaseResponse[None](
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        errors=[error.get("msg") for error in exc.errors()],
        error_details=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump()
    )


app.include_router(v1_router, prefix="/api", responses={422: {"model": AppBaseResponse[None]}})
