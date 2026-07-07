from datetime import date, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate

# ВАЖЛИВО: кожна функція приймає поточного користувача (user) і
# фільтрує/прив'язує записи за user.id (owner_id). Це гарантує,
# що один користувач ніколи не бачить і не редагує контакти іншого.


def create_contact(db: Session, body: ContactCreate, user: User) -> Contact:
    contact = Contact(**body.dict(), owner_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_contacts(db: Session, user: User, skip: int = 0, limit: int = 100) -> list[Contact]:
    return (
        db.query(Contact)
        .filter(Contact.owner_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_contact(db: Session, contact_id: int, user: User) -> Contact | None:
    return (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.owner_id == user.id)
        .first()
    )


def update_contact(
    db: Session, contact_id: int, body: ContactUpdate, user: User
) -> Contact | None:
    contact = get_contact(db, contact_id, user)
    if contact:
        for key, value in body.dict().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, user: User) -> Contact | None:
    contact = get_contact(db, contact_id, user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def search_contacts(db: Session, query: str, user: User) -> list[Contact]:
    return (
        db.query(Contact)
        .filter(
            Contact.owner_id == user.id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            ),
        )
        .all()
    )


def upcoming_birthdays(db: Session, user: User) -> list[Contact]:
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(Contact.owner_id == user.id).all()

    result = []
    for contact in contacts:
        birthday_this_year = contact.birthday.replace(year=today.year)
        if today <= birthday_this_year <= next_week:
            result.append(contact)

    return result
