from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.core.security import (
    create_access_token,
    verify_password,
)
from app.repository.base import BaseRepository, CreateSchema
from app.schema import AccessToken
from app.utils.utils import tz_now


class UserRepository(BaseRepository[models.User, CreateSchema, CreateSchema]):
    def __init__(self):
        super().__init__(models.User)

    async def authenticate_user(self, db: Session, email, password) -> AccessToken:
        try:
            # Find user by phone number
            user = db.query(models.User).filter_by(email=email).first()

            if not user or not verify_password(password, user.password):
                self.log_audit("LOGIN_FAILED", details={"phone": email})

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"message": "Invalid login credentials"},
                )

            # Update last active
            user.last_active = tz_now()
            db.commit()

            # Generate tokens
            access_token = create_access_token(user.id)

            self.log_audit("LOGIN_SUCCESS", audit_user_id=user.id)

            return access_token

        except HTTPException as e:
            raise e
        except Exception as e:
            self._handle_error(e)


user_repository = UserRepository()
