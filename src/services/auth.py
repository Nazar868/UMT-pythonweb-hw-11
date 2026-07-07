from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tokenUrl вказує клієнту, на який ендпоінт слати логін-запит.
# Сама схема OAuth2PasswordBearer змушує FastAPI/Swagger читати токен
# саме із заголовка "Authorization: Bearer <token>".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class Auth:
    pwd_context = pwd_context
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    # ---------- access token ----------
    def create_access_token(self, data: dict, expires_delta: int | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=expires_delta or settings.access_token_expire_minutes
        )
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    # ---------- email verification token ----------
    def create_email_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=settings.email_token_expire_hours)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_email_from_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "email_token":
                raise JWTError
            email = payload.get("sub")
            if email is None:
                raise JWTError
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Невірний токен для перевірки електронної пошти",
            )

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:
        """
        Дістає токен із заголовка Authorization: Bearer <token>
        (це робить сам Depends(oauth2_scheme)), валідує його і
        повертає поточного користувача. Використовується в усіх
        захищених маршрутах, щоб гарантувати, що користувач працює
        лише зі своїми даними.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не вдалося перевірити облікові дані",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "access_token":
                raise credentials_exception
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user


auth_service = Auth()
