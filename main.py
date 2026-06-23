from fastapi import FastAPI
from database import engine, Base
from routers import auth, products, categories, employees,users

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(employees.router)
app.include_router(users.router)