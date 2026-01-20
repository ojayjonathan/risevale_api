from fastapi import APIRouter, Body
from sqlalchemy.orm import Session

from app import schema
from app.repository.user import user_repository
from app.routes.deps import SessionDep

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login/", response_model=schema.AccessToken)
async def login(
    db: Session = SessionDep,
    email: str = Body(..., embed=True),
    password=Body(..., embed=True),
):
    return await user_repository.authenticate_user(db, email=email, password=password)
