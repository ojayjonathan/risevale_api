from getpass import getpass

from app.core.database import get_db
from app.models.user import User
from app.core.security import hash_password


def create_super_user():
    db = next(get_db())

    try:
        email = input("Enter email: ").strip()
        full_name = input("Enter full name: ").strip()
        password = getpass("Enter password: ")
        confirm_password = getpass("Confirm password: ")

        if password != confirm_password:
            raise ValueError("Passwords do not match")

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print("❌ User with this email already exists")
            return

        super_user = User(
            email=email,
            full_name=full_name,
            password=hash_password(password),
        )

        db.add(super_user)
        db.commit()
        db.refresh(super_user)

        print("✅ Superuser created successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    create_super_user()
