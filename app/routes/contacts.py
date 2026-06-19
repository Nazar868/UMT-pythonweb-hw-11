from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models import Contact
from app.database import SessionLocal

router = APIRouter()
db = SessionLocal()


@router.post("/contacts", status_code=201)
def create_contact(name: str, phone: str, email: str, user=Depends(get_current_user)):
    contact = Contact(
        name=name,
        phone=phone,
        email=email,
        owner_id=user["sub"]
    )
    db.add(contact)
    db.commit()
    return contact
