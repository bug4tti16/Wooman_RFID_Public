from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Date,
    DateTime,
    Column,
    Text,
    TIMESTAMP,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Relationship
from datetime import datetime, date


# declarative base class
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text(), nullable=False)
    name_jamo: Mapped[str] = mapped_column(Text(), nullable=False)
    card_number: Mapped[int] = mapped_column(nullable=True)
    card_rfid: Mapped[str] = mapped_column(Text(), nullable=True)
    active: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    use: Mapped[list["Log"]] = Relationship(back_populates="user")


class Log(Base):
    __tablename__ = "log"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP(), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    menu: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    canceled: Mapped[int] = mapped_column(nullable=False, server_default=text("0"))
    card: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = Relationship(back_populates="use")
