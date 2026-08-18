from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import jwt

from app.api.deps import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.user import User
from app import schemas
from app.core import security
from app.services.email import send_verification_email

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """
    Create a new user. Only accessible by admins.
    Triggers a background task to send a verification email.
    """
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = security.get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = security.create_email_verification_token(email=str(new_user.email))

    background_tasks.add_task(
        send_verification_email,
        receiver_email=str(new_user.email),
        token=token,
    )

    return new_user


@router.get("/verify")
def verify_user_email(token: str, db: Session = Depends(get_db)):
    """Verify a user's email address using the JWT token."""
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")  # type: ignore

        if email is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token: Email subject missing")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if bool(user.is_verified):
            return {"message": "Account is already verified!"}

        user.is_verified = True  # type: ignore
        db.commit()

        return {"message": "Successfully verified! You can now login to HAAK"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token has expired. Please request a new one.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is invalid")


@router.get("/me", response_model=schemas.UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the profile data for the currently authenticated user."""
    return current_user
