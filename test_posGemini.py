# tests/test_posGemini.py
import pytest
from backend.mvp.pos import Product, Transaction

def setup_test_inventory(db_session):
    """Helper to inject test products into the transactional database."""
    chalk = Product(sku="TEST-CHALK", name="Test Chalk", category="chalk", price_cents=1000, stock=5)
    pass_ = Product(sku="TEST-PASS", name="Test Pass", category="day_pass", price_cents=2000, stock=100)
    db_session.add_all([chalk, pass_])
    db_session.commit()
    return chalk, pass_

def test_get_inventory(client, db_session):
    setup_test_inventory(db_session)
    response = client.get("/pos/products", auth=("coach", "juniorclimbs2026"))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["sku"] == "TEST-CHALK"

def test_successful_checkout(client, db_session):
    chalk, pass_ = setup_test_inventory(db_session)
    
    payload = {
        "items": [
            {"product_id": chalk.id, "quantity": 2},
            {"product_id": pass_.id, "quantity": 1}
        ],
        "payment_method": "card"
    }
    
    response = client.post("/pos/checkout", json=payload, auth=("coach", "juniorclimbs2026"))
    assert response.status_code == 200
    data = response.json()
    
    # Verify response
    assert data["status"] == "completed"
    assert data["total_cents"] == 4000  # (2 * 1000) + (1 * 2000)
    assert "transaction_id" in data
    
    # Verify stock reduction in database
    db_session.refresh(chalk)
    assert chalk.stock == 3  # 5 - 2

def test_insufficient_stock_checkout(client, db_session):
    chalk, _ = setup_test_inventory(db_session)
    
    payload = {
        "items": [
            {"product_id": chalk.id, "quantity": 10} # Requesting 10, only 5 in stock
        ],
        "payment_method": "cash"
    }
    
    response = client.post("/pos/checkout", json=payload, auth=("coach", "juniorclimbs2026"))
    assert response.status_code == 400
    assert "Stock issue" in response.json()["detail"]
    
    # Verify stock was NOT reduced
    db_session.refresh(chalk)
    assert chalk.stock == 5
    
    # Verify NO transaction was logged
    tx_count = db_session.query(Transaction).count()
    assert tx_count == 0

def test_unauthorized_access(client):
    response = client.get("/pos/products")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"