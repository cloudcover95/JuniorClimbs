from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from backend.schemas.pos import ProductSchema, CartCheckout, TransactionSchema
from backend.mvp.pos import Product, Transaction, TransactionItem
from backend.database import SessionLocal
from backend.auth import get_current_user

router = APIRouter(prefix="/pos", tags=["POS"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/products", response_model=List[ProductSchema])
def get_inventory(category: Optional[str] = None, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    return q.all()

@router.post("/checkout")
def checkout_cart(cart: CartCheckout, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if not cart.items:
        raise HTTPException(400, "Empty cart")
    total = 0
    tx_id = str(uuid.uuid4())
    tx = Transaction(id=tx_id, total_cents=0, payment_method=cart.payment_method)
    db.add(tx)
    for item in cart.items:
        prod = db.query(Product).get(item.product_id)
        if not prod or prod.stock < item.quantity:
            raise HTTPException(400, f"Stock issue")
        prod.stock -= item.quantity
        total += prod.price_cents * item.quantity
        db.add(TransactionItem(transaction_id=tx_id, product_id=prod.id, quantity=item.quantity, unit_price_cents=prod.price_cents))
    tx.total_cents = total
    db.commit()
    return {"transaction_id": tx_id, "total_cents": total, "status": "completed", "offline_ledger": True}

@router.get("/transactions", response_model=List[TransactionSchema])
def list_daily_transactions(date: Optional[str] = Query(None), db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    q = db.query(Transaction)
    if date:
        target = datetime.strptime(date, "%Y-%m-%d").date()
        q = q.filter(Transaction.timestamp >= target, Transaction.timestamp < target + timedelta(days=1))
    return q.order_by(Transaction.timestamp.desc()).all()
