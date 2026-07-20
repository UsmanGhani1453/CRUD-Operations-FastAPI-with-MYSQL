from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine,Base
from routers import auth,products,categories,employees,users,orders

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Stripped the paths, only keeping scheme, host, and port
    allow_origins=[
        "http://127.0.0.1:5500", 
        "http://localhost:5500"
    ],
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