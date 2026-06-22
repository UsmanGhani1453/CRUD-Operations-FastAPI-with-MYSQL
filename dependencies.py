from fastapi import Depends, HTTPException
from fastapi.security import  HTTPBearer, HTTPAuthorizationCredentials
import jwt
import security
from sqlalchemy.orm import Session
from database import get_db
import models

token_auth_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme), 
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.id == user_id ).first()
    if user is None:
        raise credentials_exception
    return user