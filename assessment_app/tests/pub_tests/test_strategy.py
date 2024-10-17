import pytest
from fastapi.testclient import TestClient
from assessment_app.main import app
from assessment_app.repository.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from jose import jwt
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

# Initialize the test database
Base.metadata.create_all(bind=engine)

portfolio_id = None

@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)

@pytest.fixture
def test_portfolio_request():
    return {
        "strategy_id": "0",
        "holdings": []
    }

# Mock user authentication
def mock_get_current_user():
    return "test_user_id"

# Patch the dependencies for the test
app.dependency_overrides = {
    "assessment_app.service.auth_service.get_current_user": mock_get_current_user
}

@pytest.fixture(scope="module")
def setup_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_jwt_token(email: str):
    import pytz
    expire = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=30)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@pytest.fixture
def test_user():
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword"
    }

@pytest.fixture
def test_user_token(test_db):
    # Insert a test user in the test database
    email = "testuser@example.com"
    password_hash = "hashedpassword"
    random_salt = "random_salt"
    
    # Create user credentials entry in the test database
    test_db.execute(
        text(f"INSERT INTO user_credentials (email, password_hash, random_salt) VALUES ('{email}', '{password_hash}', '{random_salt}')"))
    test_db.commit()

    # Generate a valid JWT token for this user
    token = create_jwt_token(email)
    return token


import pytest
from fastapi.testclient import TestClient
from assessment_app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from assessment_app.repository.database import Base, get_db
from datetime import datetime, timedelta

# Use a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create the tables before running the tests
@pytest.fixture(scope="module")
def setup_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user():
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword"
    }

def test_login_user_success(test_user):
    # Send POST request to /login endpoint with valid credentials
    response = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    print(response.json())
    
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    
    cookies = response.cookies.get("jwt_token")
    assert cookies is not None
    assert cookies.startswith("Bearer ")


def test_get_strategies():
    response = client.get("/strategies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["id"] == "0"
    assert data[0]["name"] == "default"

def test_create_portfolio(test_portfolio_request):
    response = client.post("/portfolio", json=test_portfolio_request)
    assert response.status_code == 200
    data = response.json()
    portfolio_id = data["id"]
    assert data["strategy_id"] == test_portfolio_request["strategy_id"]
    assert data["cash_remaining"] == 1000000.0  # Default cash for a new portfolio


def test_create_portfolio_with_holdings(setup_db, test_user):
    # Register the user
    client.post("/register", json=test_user)

    # Define the portfolio request with holdings
    portfolio_request = {
        "strategy_id": "strategy_123",
        "cash_remaining": 50000.0,
        "holdings": [
            {"stock_symbol": "AAPL", "quantity": 10, "purchase_price": 150.0},
            {"stock_symbol": "GOOGL", "quantity": 5, "purchase_price": 2000.0}
        ]
    }

    # Create the portfolio
    response = client.post("/portfolio", json=portfolio_request)
    assert response.status_code == 200
    data = response.json()

    # Check portfolio values
    assert data["cash_remaining"] == 50000.0

    # Check holdings
    assert len(data["holdings"]) == 2
    assert data["holdings"][0]["stock_symbol"] == "AAPL"
    assert data["holdings"][1]["stock_symbol"] == "GOOGL"


def test_get_portfolio_by_id():
    # Assuming there is already a portfolio with id "test_portfolio_id"
    response = client.get(f"/portfolio/{portfolio_id}?current_ts=2024-01-01T00:00:00")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == portfolio_id

def test_delete_portfolio():
    response = client.delete(f"/portfolio/{portfolio_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == portfolio_id

def test_get_net_worth():
    portfolio_id = "test_portfolio_id"
    response = client.get(f"/portfolio-net-worth?portfolio_id={portfolio_id}")
    assert response.status_code == 200
    net_worth = response.json()
    assert isinstance(net_worth, float)
    assert net_worth >= 0.0
