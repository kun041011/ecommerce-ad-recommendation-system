from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, products, orders, community, behavior

app = FastAPI(title="E-Commerce Ad Recommendation System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(community.router)
app.include_router(behavior.router)


def init_db():
    import os
    os.makedirs("data", exist_ok=True)
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
