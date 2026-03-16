"""
PyTest Configuration and Fixtures for InvestAI Backend Tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app
from models.user import User
from models.portfolio import Portfolio
from models.holding import Holding
from auth.jwt_handler import get_password_hash, create_access_token


# Test database URL - use SQLite for fast testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Generate a valid JWT token for the test user"""
    token = create_access_token(data={"sub": test_user.email, "user_id": test_user.id})
    return token


@pytest.fixture
def auth_headers(test_user_token):
    """Return authorization headers with test user token"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def test_portfolio(db_session, test_user):
    """Create a test portfolio"""
    portfolio = Portfolio(
        user_id=test_user.id,
        name="Test Portfolio",
        description="A test portfolio",
        is_active=True
    )
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    return portfolio


@pytest.fixture
def test_holding(db_session, test_portfolio):
    """Create a test holding"""
    holding = Holding(
        portfolio_id=test_portfolio.id,
        symbol="BBCA",
        shares=100,
        avg_cost=9000,
        sector="Financials",
        industry="Banking"
    )
    db_session.add(holding)
    db_session.commit()
    db_session.refresh(holding)
    return holding


@pytest.fixture
def second_user(db_session):
    """Create a second test user"""
    user = User(
        email="second@example.com",
        password_hash=get_password_hash("secondpassword123"),
        full_name="Second User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user_token(second_user):
    """Generate a valid JWT token for the second user"""
    token = create_access_token(data={"sub": second_user.email, "user_id": second_user.id})
    return token


# Mock fixtures for external services

@pytest.fixture
def mock_stock_price():
    """Mock stock price data"""
    return {
        "symbol": "BBCA",
        "price": 9500.0,
        "change": 100.0,
        "change_pct": 1.05,
        "open": 9400.0,
        "high": 9550.0,
        "low": 9380.0,
        "volume": 15000000,
        "timestamp": "2026-03-15T10:00:00"
    }


@pytest.fixture
def mock_ai_response():
    """Mock AI response"""
    return {
        "response": "Based on your portfolio analysis, BBCA is a strong hold position.",
        "tokens_used": 150,
        "response_time_ms": 500
    }
