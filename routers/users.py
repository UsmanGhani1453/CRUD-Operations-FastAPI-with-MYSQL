from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas, database
import security
from email_utils import send_verification_email
import jwt
from dependencies import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db),
                admin_user: models.User = Depends(get_current_admin)):
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = security.create_email_verification_token(email=str(new_user.email))  
    send_verification_email(receiver_email=str(new_user.email), token=token)

    return new_user

@router.get("/verify")
def verify_user_email(token: str, db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub") # type: ignore
        
        if email is None:
            raise HTTPException(status_code=400, detail="Invalid Token")

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Wrap in bool() to fix Pylance Column[bool] conditional error
        if bool(user.is_verified):
            return {"message": "Account is already verified!"}
            
        # Add type: ignore to fix Pylance assignment error
        user.is_verified = True # type: ignore
        db.commit()
        
        return {"message": "Successfully verified! You can now login to HAAK"}
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Token is expired or is invalid")