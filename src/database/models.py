from datetime import date, datetime

from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import func

from src.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    avatar = Column(String(255), nullable=True)

    confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())

    contacts = relationship(
        "Contact", back_populates="owner", cascade="all, delete-orphan"
    )


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(String(255), nullable=True)

    # Прив'язка контакту до конкретного власника (користувача).
    # Саме це поле забезпечує, що користувач бачить і керує лише
    # своїми контактами.
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="contacts")
