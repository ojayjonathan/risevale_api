import logging
import os
import time

from fastapi import (
    FastAPI,
)
from fastapi import (
    HTTPException,
    Request,
    Depends,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse
from psycopg2 import errors as psycopg2_errors
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.staticfiles import StaticFiles

from app import schema
from app.core.config import get_settings
from app.core.database import get_db
from app.routes.deps import validate_auth_cookie
from app.routes.main import router
from app.routes.swagger import swagger_router

logger = logging.getLogger(__name__)
settings = get_settings()

os.environ["TZ"] = "Africa/Nairobi"
time.tzset()

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    responses={
        400: {"model": schema.ErrorResponse},
        500: {"model": schema.ErrorResponse},
        422: {"model": schema.ErrorResponse},
        403: {"model": schema.ErrorResponse},
    },
)


@app.get("/openapi.json", tags=["docs"], include_in_schema=False)
async def openapi(
    user=Depends(validate_auth_cookie),
):
    if not user:
        return RedirectResponse(url="/docs/login?next_url=/openapi.json")

    return get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request,
    exc: RequestValidationError,
):
    errors = {}
    message = "Fix the following errors:"
    for e in exc.errors():
        errors[e["loc"][-1]] = {"message": e["msg"], "msg": e["msg"], "type": e["type"]}
        message += f"\n   {str(e['loc'][-1]).replace('_', ' ')}: {e['msg']}"

    return JSONResponse({"detail": errors, "message": message}, status_code=422)


@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request,
    exc: ValidationError,
):
    errors = {}
    message = "Fix the following errors:"
    for e in exc.errors():
        errors[e["loc"][-1]] = {"message": e["msg"], "msg": e["msg"], "type": e["type"]}
        message += f"\n     {e['loc'][-1]}: {e['msg']}"

    return JSONResponse({"detail": errors, "message": message}, status_code=422)


def format_error(message, detail):
    if isinstance(message, str):
        message_ = message
    else:
        message_ = f"An error occurred while processing your request, please try again later or contact our support"

    detail_ = {}
    if isinstance(detail, dict):
        detail_ = detail
    elif isinstance(detail, list) or isinstance(detail, tuple):
        detail_ = {message: ",".join(detail)}

    return {
        "message": message_,
        "detail": detail_,
        "precondition": detail_.get("precondition"),
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: object, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return JSONResponse(
            format_error(
                message=exc.detail.get("message"),
                detail=exc.detail.get("detail"),
            ),
            status_code=exc.status_code,
        )

    return JSONResponse(
        {"detail": {}, "message": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (SQLAlchemyError, psycopg2_errors.DatabaseError)):
        db = get_db().__next__()
        db.rollback()

    logging.error(exc, exc_info=exc)
    return JSONResponse(
        format_error(
            message="An error occurred while processing your request, please try again later or contact our support",
            detail={},
        ),
        status_code=500,
    )


media_dir = os.path.join(os.getcwd(), settings.MEDIA_BASE)
if not os.path.exists(media_dir):
    os.mkdir(media_dir)

app.mount(
    "/media",
    StaticFiles(directory=media_dir),
    name="media",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "PUT", "OPTIONS", "DELETE", "PATCH", "GET"],
    allow_headers=["*"],
)


app.include_router(router)
app.include_router(swagger_router)
