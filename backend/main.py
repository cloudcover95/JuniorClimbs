from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database import init_db, SessionLocal
from backend.mvp.pos import Product
from backend.routers import athletes as athletes_router, practices as practices_router, pos as pos_router
from backend.services.bitnet_iot import bitnet_service
from backend.auth import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            seed_products = [
                Product(sku="DP-DAY", name="Full Day Pass", category="day_pass", price_cents=2800, stock=200, description="Unlimited climbing + gear access"),
                Product(sku="CHALK-8", name="Chalk 8oz Block", category="chalk", price_cents=950, stock=120, description="Performance gym chalk"),
                Product(sku="SHOE-RENT", name="Rental Shoes", category="shoes", price_cents=1450, stock=65, description="Beginner rental"),
                Product(sku="SHOE-PERF", name="Performance Lace Shoes", category="shoes", price_cents=2150, stock=35, description="Advanced climbing shoes"),
            ]
            db.add_all(seed_products)
            db.commit()
            print("[POS] Climbing gym inventory seeded")
    finally:
        db.close()
    bitnet_service.start()
    yield
    bitnet_service.stop()

app = FastAPI(title="JuniorClimbs", version="0.5.0-edge", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(athletes_router.router)
app.include_router(practices_router.router)
app.include_router(pos_router.router)

@app.get("/")
def root():
    return {"message": "JuniorClimbs edge-native coaching + POS platform live", "bitnet": "active", "offline_ledger": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
