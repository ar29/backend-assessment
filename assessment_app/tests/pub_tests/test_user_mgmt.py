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

@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(test_db):
    # Insert a test user into the database
    email = "testuser@example.com"
    password_hash = "hashedpassword"  # This would normally be hashed
    random_salt = "random_salt"
    
    test_db.execute(
        "INSERT INTO usercredentials (email, password_hash, random_salt) VALUES (:email, :password_hash, :random_salt)",
        {"email": email, "password_hash": password_hash, "random_salt": random_salt}
    )
    test_db.commit()

    return {"username": email, "password": "hashedpassword"}

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
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "testpassword"
    }

def test_register_user(setup_db, test_user):
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["first_name"] == test_user["first_name"]
    assert data["last_name"] == test_user["last_name"]

def test_register_existing_user(setup_db, test_user):
    # Register the user for the first time
    client.post("/register", json=test_user)

    # Try registering the same user again
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "User with this email already exists"}

def test_login_user_success(test_user):
    # Send POST request to /login endpoint with valid credentials
    response = client.post("/login", data=test_user)
    
    assert response.status_code == 200
    assert response.json() == {"message": "Login successful"}
    
    cookies = response.cookies.get("jwt_token")
    assert cookies is not None
    assert cookies.startswith("Bearer ")

def test_login_user_invalid_credentials():
    # Send POST request to /login endpoint with invalid credentials
    response = client.post("/login", data={"username": "wrong@example.com", "password": "wrongpassword"})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_login_user_missing_credentials():
    # Send POST request to /login endpoint with missing credentials
    response = client.post("/login", data={"username": "", "password": ""})
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"