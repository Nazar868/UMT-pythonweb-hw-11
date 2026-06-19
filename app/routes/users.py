from fastapi import APIRouter, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.dependencies import get_current_user

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/me")
@limiter.limit("5/minute")
def me(user=Depends(get_current_user)):
    return user
