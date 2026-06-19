from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from pydantic import BaseModel


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        index=True
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2)
    )

    stock: Mapped[int] = mapped_column(
        default=0
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id")
    )

    category = relationship(
        "Category",
        back_populates="products"
    )