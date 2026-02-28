from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.init_db import init_db
from app.db.session import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

# App instance
app = FastAPI(
    title="Arithmetica API",
    description="Secure multi-tenant arithmetic SaaS backend",
    version="1.0.0",
)

# CORS configuration (needed for frontend later)
origins = [
    "http://localhost:5173",  # React default dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "Arithmetica backend running 🚀"}