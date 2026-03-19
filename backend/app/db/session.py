# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

# suing pool_pre_ping to avoid stale connections 

engine = create_engine(settings.mysql_url, pool_pre_ping=True, future=True)
SessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    provide a DB session for fastapi dependency injection
    usage: 
        db = Depends(get_db)

    Ensure to close the session in finally block
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        