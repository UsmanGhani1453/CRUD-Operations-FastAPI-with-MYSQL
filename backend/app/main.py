from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import CORS_ALLOWED_ORIGINS
from app.api.routes import auth, users, products, categories, employees, orders

app = FastAPI(title="HAAK CRUD API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(employees.router)
app.include_router(orders.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
