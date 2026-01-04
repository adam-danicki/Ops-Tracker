from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import DATABASE_URL

# Create one engine for the entire application
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,   
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Base class for models(tables)
class Base(DeclarativeBase):
    pass

# FastAPI dependency: gives db a session to request, then closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()