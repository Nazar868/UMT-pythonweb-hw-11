from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserCreate, UserResponse, TokenResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Реєстрація нового користувача.
    - Якщо email вже зайнятий -> 409 Conflict.
    - Пароль хешується (bcrypt) і ніколи не зберігається у відкритому вигляді.
    - Після реєстрації на пошту надсилається лист з посиланням для
      підтвердження email.
    """
    exist_user = repository_users.get_user_by_email(db, body.email)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Обліковий запис із таким email вже існує",
        )

    new_user = repository_users.create_user(db, body)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Логін приймає дані форми (username = email, password) і повертає
    access_token, який далі передається клієнтом у заголовку
    "Authorization: Bearer <access_token>".
    """
    user = repository_users.get_user_by_email(db, body.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильний email або пароль"
        )

    if not auth_service.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильний email або пароль"
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронну пошту не підтверджено",
        )

    access_token = auth_service.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(token)
    user = repository_users.get_user_by_email(db, email)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Помилка верифікації")

    if user.confirmed:
        return {"message": "Електронну пошту вже підтверджено"}

    repository_users.confirm_email(db, email)
    return {"message": "Електронну пошту підтверджено"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """Повторна відправка листа підтвердження email."""
    user = repository_users.get_user_by_email(db, body.email)

    if user and not user.confirmed:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )

    return {"message": "Перевірте свою електронну пошту для підтвердження"}
