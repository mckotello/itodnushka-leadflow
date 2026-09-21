from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    name: Mapped[str] = mapped_column(
        String(100)
    )

    company: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    contact: Mapped[str] = mapped_column(
        String(200)
    )

    message: Mapped[str] = mapped_column(
        Text
    )

    budget: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
    )

    ai_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )

    ai_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_priority: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    ai_features: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ai_estimate: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )