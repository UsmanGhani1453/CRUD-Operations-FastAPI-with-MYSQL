import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import APP_BASE_URL
from app.models.user import User
from app.models.product import Product
from app import schemas
from app.db.session import get_db
from app.api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/products", tags=["Products"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads")


@router.post("/upload-image")
async def upload_product_image(
    file: UploadFile = File(...),
    admin_user: User = Depends(get_current_admin),
):
    """
    Accepts a single image file from the admin panel, saves it to disk
    under a random filename (so uploads can't collide or overwrite each
    other), and returns the public URL to store on a product's image_url.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use JPEG, PNG, WEBP, or GIF.",
        )

    contents = await file.read()
    if len(contents) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be smaller than 5MB.")

    ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    with open(os.path.join(UPLOADS_DIR, filename), "wb") as f:
        f.write(contents)

    return {"url": f"{APP_BASE_URL}/uploads/{filename}"}


@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_product = Product(**product.model_dump(), owner_id=admin_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/", response_model=list[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return db.query(Product).offset(skip).limit(limit).all()


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = product.name  # type: ignore
    db_product.price = product.price  # type: ignore
    db_product.stock = product.stock  # type: ignore
    db_product.extra_data = product.extra_data  # type: ignore
    db_product.image_url = product.image_url  # type: ignore

    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}
