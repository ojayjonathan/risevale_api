from logging import getLogger

from fastapi import Depends, Security, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app import models
from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.repository.user import user_repository

logger = getLogger()

auth_token_bearer = HTTPBearer(auto_error=True)

SessionDep: Session = Depends(get_db)


def current_user(
    credentials: HTTPBasicCredentials = Security(auth_token_bearer),
    db: Session = SessionDep,
    settings: Settings = Depends(get_settings),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_exception
    if access_token := decode_access_token(credentials.credentials, settings=settings):
        if user := user_repository.get(db=db, id=int(access_token.sub)):
            return user

    raise credentials_exception


def validate_auth_cookie(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    authorization_cookie = request.cookies.get("authorization")
    if authorization_cookie:
        if access_token := decode_access_token(authorization_cookie, settings=settings):
            db = next(get_db())
            if user := user_repository.get(db=db, id=int(access_token.sub)):
                return user
    return None
