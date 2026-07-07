from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.user import UserCreate
from src.services.auth import auth_service


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, body: UserCreate) -> User:
    hashed_password = auth_service.get_password_hash(body.password)
    new_user = User(
        username=body.username,
        email=body.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def confirm_email(db: Session, email: str) -> None:
    user = get_user_by_email(db, email)
    if user:
        user.confirmed = True
        db.commit()


def update_avatar(db: Session, email: str, url: str) -> User:
    user = get_user_by_email(db, email)
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user
