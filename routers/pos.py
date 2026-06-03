# routers/pos.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from mvp.pos import Product, Transaction, TransactionItem
from schemas.pos import ProductSchema, CartCheckout, TransactionSchema
from main import get_db, get_current_user

router = APIRouter(prefix="/pos", tags=["POS"])

@router.get("/products", response_model=List[ProductSchema])
def get_inventory(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    q = db.query(Product)
    if category:
        q = q.filter(Product.category == category)
    return q.all()

@router.post("/checkout")
def checkout_cart(
    cart: CartCheckout,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_cents = 0
    tx_id = str(__import__("uuid").uuid4())
    tx = Transaction(
        id=tx_id,
        total_cents=0,
        payment_method=cart.payment_method,
        status="completed"
    )
    db.add(tx)

    for item in cart.items:
        prod = db.query(Product).get(item.product_id)
        if not prod or prod.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item.product_id}")
        prod.stock -= item.quantity
        total_cents += prod.price_cents * item.quantity
        db.add(TransactionItem(
            transaction_id=tx_id,
            product_id=prod.id,
            quantity=item.quantity,
            unit_price_cents=prod.price_cents
        ))

    tx.total_cents = total_cents
    db.commit()

    response: Dict[str, Any] = {
        "transaction_id": tx_id,
        "total_cents": total_cents,
        "status": "completed",
        "payment_method": cart.payment_method,
        "offline_ledger": True
    }

    if cart.payment_method == "crypto":
        response["crypto"] = {
            "tx_hash": cart.crypto_tx_hash or "pending_brave_wallet",
            "wallet_address": cart.crypto_wallet_address,
            "note": "Recorded for later on-chain verification. Market via .brave domains."
        }

    return response

@router.get("/transactions", response_model=List[TransactionSchema])
def list_daily_transactions(
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    q = db.query(Transaction)
    if date:
        try:
            target = datetime.strptime(date, "%Y-%m-%d").date()
            q = q.filter(Transaction.timestamp >= target, Transaction.timestamp < target + timedelta(days=1))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    return q.order_by(Transaction.timestamp.desc()).all()