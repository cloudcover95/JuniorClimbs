# mvp/pos.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
import uuid
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    price_cents: Mapped[int] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(default=None)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    total_cents: Mapped[int] = mapped_column(default=0, nullable=False)
    payment_method: Mapped[str] = mapped_column(default="cash")
    status: Mapped[str] = mapped_column(default="completed")
    items: Mapped[List["TransactionItem"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")

class TransactionItem(Base):
    __tablename__ = "transaction_items"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_id: Mapped[str] = mapped_column(nullable=False)
    product_id: Mapped[int] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(nullable=False)
    transaction: Mapped["Transaction"] = relationship(back_populates="items")