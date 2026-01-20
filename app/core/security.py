from datetime import datetime, timedelta

from jose import jwt
from passlib import context

from app import schema
from app.core.config import Settings, get_settings
from app.schema import AccessTokenData

pwd_context = context.CryptContext(schemes=["sha256_crypt"])
ALGORITHM = "HS256"


def create_access_token(
    subject,
    settings: Settings = get_settings(),
) -> schema.AccessToken:
    exp = datetime.now() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXP_MINUTES,
    )
    token = jwt.encode(
        {"exp": exp, "sub": str(subject)},
        key=settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return schema.AccessToken(
        access_token=token, refresh_token=create_refresh_token(subject)
    )


def decode_access_token(
    token: str | None,
    settings: Settings = get_settings(),
) -> AccessTokenData | None:
    try:
        if token:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

            return schema.AccessTokenData(
                exp=payload["exp"], sub=payload["sub"], payload=payload
            )
    except Exception:
        return None


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_refresh_token(
    subject: str | int,
    settings: Settings = get_settings(),
) -> str:
    exp = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXP_DAYS)
    return jwt.encode(
        {"exp": exp, "sub": str(subject), "type": "refresh"},
        key=settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
