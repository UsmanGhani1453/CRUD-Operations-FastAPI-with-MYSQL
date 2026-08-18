from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.category import Category
from app import schemas
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_category = Category(**category.model_dump(), owner_id=admin_user.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/", response_model=list[schemas.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Category).offset(skip).limit(limit).all()


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_category = db.query(Category).filter(Category.id == category_id).first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db_category.name = category.name  # type: ignore
    db_category.description = category.description  # type: ignore
    db_category.extra_data = category.extra_data  # type: ignore

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_category = db.query(Category).filter(Category.id == category_id).first()

    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}
