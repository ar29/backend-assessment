from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from assessment_app.models.models import User, RegisterUserRequest
from assessment_app.repository.database import get_db
from assessment_app.models.schema import UserCredentials
from assessment_app.service.auth_service import SECRET_KEY, ALGORITHM


router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/register", response_model=User)
async def register_user(user: RegisterUserRequest, db: Session = Depends(get_db)) -> User:
    """
    Register a new user in database and save the login details (email_id and password) separately from User.
    Also, do necessary checks as per your knowledge.
    """
    try:
        print(user)
        # Check if the user already exists
        existing_user = db.query(UserCredentials).filter(UserCredentials.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Hash the password
        password_hash = get_password_hash(user.password)

        # Create user credentials entry
        new_user_credentials = UserCredentials(email=user.email, password_hash=password_hash, random_salt="random_salt")
        db.add(new_user_credentials)
        db.commit()

        # Create the User response (without password)
        new_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name)
        
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def verify_user_credentials(db: Session, email: str, password: str):
    """
    Verify if the user's credentials are correct by checking the email and password_hash.
    """
    user = db.query(UserCredentials).filter(UserCredentials.email == email).first()
    if not user or user.password_hash != password:  # Assuming password is already hashed
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def create_jwt_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=str)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Login user after verification of credentials and add jwt_token in response cookies.
    Also, do necessary checks as per your knowledge.
    """
     
    # Verify user credentials
    user = verify_user_credentials(db, form_data.username, form_data.password)

    # Create JWT token
    jwt_token = create_jwt_token(user.email)

    # Create response with JWT token in cookies
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="jwt_token", value=f"Bearer {jwt_token}", httponly=True)

    return response