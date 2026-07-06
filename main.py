from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, products, categories, employees,users,orders


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(employees.router)
app.include_router(users.router)
app.include_router(orders.router)