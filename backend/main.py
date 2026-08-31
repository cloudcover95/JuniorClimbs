# backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import uvicorn

from backend.database import init_db, SessionLocal
from backend.mvp.pos import Product
from backend.routers import pos as pos_router, athletes as athletes_router, practices as practices_router
from backend.routers import stonefield as stonefield_router
from backend.routers import navmesh as navmesh_router
from backend.routers import forum as forum_router
from backend.routers import sphere as sphere_router
from backend.routers import source as source_router
from backend.models_stonefield import StoneField  # noqa: F401
from backend.models_navmesh import TilePack  # noqa: F401
from backend.models_forum import CrowdEvent  # noqa: F401
from backend.models_sphere import ArenaNode  # noqa: F401
from backend.models_source import SourceProject  # noqa: F401
from backend.services.bitnet_iot import bitnet_service
from backend.auth import get_current_user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "coach" or credentials.password != "juniorclimbs2026":
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid coach credentials")
    return credentials.username

def _bitnet_log_callback(event_type: str, payload: dict):
    print("[BitNet][LOG]", event_type, payload)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            seed = [
                Product(sku="DP-DAY", name="Full Day Pass", category="day_pass", price_cents=2800, stock=200),
                Product(sku="CHALK-8", name="Chalk 8oz Block", category="chalk", price_cents=950, stock=120),
                Product(sku="SHOE-RENT", name="Rental Shoes", category="shoes", price_cents=1450, stock=65),
                Product(sku="SHOE-PERF", name="Performance Lace Shoes", category="shoes", price_cents=2150, stock=35),
            ]
            db.add_all(seed)
            db.commit()
        from backend.seed_red_feather import ensure_red_feather_seed
        from backend.seed_navmesh import ensure_navmesh_seed
        from backend.seed_sphere import ensure_sphere_seed
        from backend.seed_front_range import ensure_front_range_seed
        ensure_red_feather_seed(db)
        ensure_navmesh_seed(db)
        ensure_sphere_seed(db)
        ensure_front_range_seed(db)
    finally:
        db.close()

    bitnet_service.register_log_callback(_bitnet_log_callback)
    bitnet_service.start()
    yield
    bitnet_service.stop()

app = FastAPI(title="JuniorClimbs", version="0.9.1-edge", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pos_router.router)
app.include_router(athletes_router.router)
app.include_router(practices_router.router)
app.include_router(stonefield_router.router)
app.include_router(navmesh_router.router)
app.include_router(forum_router.router)
app.include_router(sphere_router.router)
app.include_router(source_router.router)

@app.get("/")
def root():
    return {
        "message": "JuniorClimbs — Front Range seeds + SourceLedger",
        "offline": True,
        "vendor_links": False,
        "fields": "/stonefield/fields",
        "source": "/source/schema",
        "arenas": "/arena",
    }

@app.get("/bitnet/status")
def bitnet_status(user: str = Depends(get_current_user)):
    return {
        "running": bitnet_service.running,
        "inference_active": bitnet_service.thread is not None and bitnet_service.thread.is_alive(),
        "note": "Gym IoT BitNet + FieldCore + licensed community source",
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
