from typing import Any, Annotated

from pydantic import BaseModel, Field, EmailStr

from app.utils.utils import normalize_phone_number


class AccessToken(BaseModel):
    type: Annotated[
        str | None, Field(default="Bearer", description="Type of the token")
    ] = None
    access_token: str
    refresh_token: Annotated[
        str | None, Field(default="", description="Refresh token for the access token")
    ] = None


class AccessTokenData(BaseModel):
    exp: float
    sub: Any
    payload: dict


class Login(BaseModel):
    phone_number: Annotated[
        str | None, Field(..., description="Phone number of the user")
    ] = None
    password: Annotated[
        str | None,
        Field(..., min_length=6, max_length=30, description="Password of the user"),
    ] = None

    def __init__(self, **data):
        if "phone_number" in data:
            data["phone_number"] = normalize_phone_number(data["phone_number"])

        super().__init__(**data)


class PasswordResetInit(BaseModel):
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetComplete(BaseModel):
    reset_code: str
    new_password: Annotated[
        str | None,
        Field(
            ..., min_length=6, max_length=30, description="New password for the user"
        ),
    ] = None
    email_or_phone: Annotated[
        str | None, Field(description="Email or phone number for password reset")
    ] = None
