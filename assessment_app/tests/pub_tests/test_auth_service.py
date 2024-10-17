import pytest
from fastapi.testclient import TestClient
from jose import jwt
from assessment_app.main import app
from assessment_app.repository.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from datetime import datetime, timedelta

# Use a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the test database
Base.metadata.create_all(bind=engine)

client = TestClient(app)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

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

app.dependency_overrides[get_db] = override_get_db

def create_jwt_token(email: str):
    import pytz
    expire = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=30)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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

def test_get_current_user_valid_token(test_user_token):
    # Set cookie with the JWT token in the client request
    client.cookies.set("jwt_token", test_user_token)
    
    response = client.get("/strategies")
    assert response.status_code == 200
    assert response.json() == [{'id': '0', 'name': 'default'}]

def test_get_current_user_invalid_token():
    invalid_token = "invalid_token"
    
    # Set cookie with the invalid JWT token
    client.cookies.set("jwt_token", invalid_token)
    
    response = client.get("/strategies")
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_get_current_user_missing_token():
    # Ensure no cookies are set
    client.cookies.clear()
    
    response = client.get("/strategies")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing token"
