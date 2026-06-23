from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, security
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Authentication"])

# The POST /users/ route has been removed to avoid conflict with users.py

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Generate the JWT access token
    access_token = security.create_access_token(data={"sub": user.email, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}