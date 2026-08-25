import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import CORS_ALLOWED_ORIGINS
from app.api.routes import auth, users, products, categories, employees, orders

app = FastAPI(title="HAAK CRUD API")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend origins for testing/presentation
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploaded product images are saved to disk here and served back out as
# plain static files at /uploads/<filename> (see products.upload_product_image).
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
# os.makedirs(UPLOADS_DIR, exist_ok=True)
# app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(employees.router)
app.include_router(orders.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
