# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.models import Base
from app.db.session import get_db

# Shared in-memory SQLite database across all connections
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once for the shared Base
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the app's get_db dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def SessionLocal():
    """
    Gives access to the shared TestingSessionLocal factory.
    """
    return TestingSessionLocal


@pytest.fixture
def db(SessionLocal):
    """
    Yields an isolated DB session per test.
    Recreates schema each time to avoid cross-test state leakage.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    """
    Shared FastAPI test client for all tests.
    """
    return TestClient(app)
