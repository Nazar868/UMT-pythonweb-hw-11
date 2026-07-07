from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repository_contacts.create_contact(db, contact, current_user)


@router.get("/", response_model=list[ContactResponse])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repository_contacts.get_contacts(db, current_user, skip, limit)


@router.get("/search/", response_model=list[ContactResponse])
def search_contacts(
    query: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repository_contacts.search_contacts(db, query, current_user)


@router.get("/birthdays/", response_model=list[ContactResponse])
def upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repository_contacts.upcoming_birthdays(db, current_user)


@router.get("/{contact_id}", response_model=ContactResponse)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = repository_contacts.get_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = repository_contacts.update_contact(db, contact_id, body, current_user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = repository_contacts.delete_contact(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")
    return None
