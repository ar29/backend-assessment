from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy.orm import Session
from assessment_app.models.constants import JWT_TOKEN
from assessment_app.repository.database import get_db
from assessment_app.models.schema import UserCredentials

# Secret key and algorithm (usually these would be in a config file)
SECRET_KEY = "your_secret_key"  # Replace this with a more secure key
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_token(token: str, db: Session) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if the token exists in the database
        user = db.query(UserCredentials).filter(UserCredentials.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")



def get_current_user(request: Request, db: Session = Depends(get_db)) -> str:
    """
    Get jwt_token from request cookies from database and return corresponding user id which is `email_id` to keep it simple.
    Verify the jwt_token is authentic (from database) and is not expired.
    """
    token = request.cookies.get(JWT_TOKEN)
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    return verify_token(token, db)
