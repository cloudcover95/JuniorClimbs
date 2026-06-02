from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class ProductSchema(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    price_cents: int
    stock: int
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class TransactionItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=100)

class CartCheckout(BaseModel):
    items: List[TransactionItemCreate]
    payment_method: str = Field(default="cash", pattern="^(cash|card|member)$")

class TransactionItemSchema(BaseModel):
    product_id: int
    quantity: int
    unit_price_cents: int
    model_config = ConfigDict(from_attributes=True)

class TransactionSchema(BaseModel):
    id: str
    timestamp: datetime
    total_cents: int
    payment_method: str
    status: str
    items: List[TransactionItemSchema]
    model_config = ConfigDict(from_attributes=True)
