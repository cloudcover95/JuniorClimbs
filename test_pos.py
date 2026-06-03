# tests/test_pos.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal, init_db
from backend.mvp.pos import Product

@pytest.fixture(scope="function")
def transactional_db():
    """Existing transactional fixture - rolls back after each test"""
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_checkout_success(client, transactional_db):
    # Ensure at least one product exists
    if transactional_db.query(Product).count() == 0:
        transactional_db.add(Product(sku="TEST-01", name="Test Pass", category="day_pass", price_cents=1000, stock=10))
        transactional_db.commit()
    product = transactional_db.query(Product).first()
    payload = {
        "items": [{"product_id": product.id, "quantity": 1}],
        "payment_method": "cash"
    }
    response = client.post("/pos/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transaction_id" in data
    assert data["total_cents"] == product.price_cents
    assert data["payment_method"] == "cash"
    assert data["offline_ledger"] is True

def test_checkout_insufficient_stock(client, transactional_db):
    product = transactional_db.query(Product).first()
    payload = {
        "items": [{"product_id": product.id, "quantity": 9999}],
        "payment_method": "cash"
    }
    response = client.post("/pos/checkout", json=payload)
    assert response.status_code == 400
    assert "stock" in response.json()["detail"].lower() or "insufficient" in response.json()["detail"].lower()

def test_list_daily_transactions(client, transactional_db):
    response = client.get("/pos/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_checkout_crypto_via_brave(client, transactional_db):
    product = transactional_db.query(Product).first()
    payload = {
        "items": [{"product_id": product.id, "quantity": 1}],
        "payment_method": "crypto",
        "crypto_tx_hash": "0xbrave123abc",
        "crypto_wallet_address": "brave-wallet-addr"
    }
    response = client.post("/pos/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["payment_method"] == "crypto"
    assert "crypto" in data
    assert data["crypto"]["tx_hash"] == "0xbrave123abc"