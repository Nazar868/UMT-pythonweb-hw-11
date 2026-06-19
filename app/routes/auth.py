from fastapi import APIRouter, HTTPException
from passlib.hash import bcrypt
from app.models import User
from app.database import SessionLocal
from app.auth import create_access_token

router = APIRouter()
db = SessionLocal()


@router.post("/register", status_code=201)
def register(email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=409, detail="User exists")

    new_user = User(
        email=email,
        hashed_password=bcrypt.hash(password)
    )
    db.add(new_user)
    db.commit()

    return {"email": email}


@router.post("/login")
def login(email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not bcrypt.verify(password, user.hashed_password):
        raise HTTPException(status_code=401)

    token = create_access_token({"sub": user.email})
    return {"access_token": token}
