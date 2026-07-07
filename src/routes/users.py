from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.services.avatar import avatar_service
from src.services.limiter import limiter

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def read_my_profile(
    request: Request,
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Повертає дані поточного авторизованого користувача.
    Обмежено 5 запитами на хвилину з однієї IP-адреси
    (slowapi), щоб маршрут не можна було зловживати.
    """
    return current_user


@router.patch("/avatar", response_model=UserResponse)
def update_avatar_user(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """Завантажує новий аватар користувача у Cloudinary і зберігає URL у БД."""
    avatar_url = avatar_service.upload_avatar(file.file, current_user.username)
    updated_user = repository_users.update_avatar(db, current_user.email, avatar_url)
    return updated_user
