from typing import Optional

from fastapi import (
    Form,
    Request,
    Depends,
    APIRouter,
)
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.security import create_access_token, verify_password
from app.repository.user import user_repository
from app.routes.deps import validate_auth_cookie, SessionDep
from app.utils.utils import render_template

swagger_router = APIRouter()


@swagger_router.get("/docs", include_in_schema=False, tags=["docs"])
async def get_swagger_documentation(user=Depends(validate_auth_cookie)):
    if not user:
        return RedirectResponse(url="/docs/login?next_url=/docs")

    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@swagger_router.get(
    "/redoc",
    include_in_schema=False,
)
async def get_redoc_documentation(
    user=Depends(validate_auth_cookie),
):
    if not user:
        return RedirectResponse(url="/docs/login?next_url=/redoc")

    if not user.is_developer:
        return HTMLResponse("<h3>Unauthorized</h3>")

    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@swagger_router.post(
    "/docs/login", response_class=HTMLResponse, include_in_schema=False
)
@swagger_router.get("/docs/login", response_class=HTMLResponse, include_in_schema=False)
async def auth_login(
    request: Request,
    next_url: Optional[str] = None,
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None, min_length=6, max_length=30),
    db=SessionDep,
):
    error = None
    if request.method == "POST":
        user = user_repository.filter_by(db, email=email).first()
        if user and verify_password(password, user.password):
            access_token = create_access_token(user.id)

            redirect_url = next_url or "/docs"
            response = RedirectResponse(url=redirect_url, status_code=303)
            response.set_cookie(key="authorization", value=access_token.access_token)

            return response
        else:
            error = "Invalid login credential"

    return render_template("login.html", {"request": request, "error": error})
