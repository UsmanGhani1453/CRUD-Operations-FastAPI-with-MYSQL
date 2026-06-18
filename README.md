# FastAPI + MySQL Employee Management API

A secure, modular, and robust RESTful API built with FastAPI, SQLAlchemy (MySQL), and JWT Authentication.

## 🚀 Key Features

* **Secure Authentication**: Industry-standard JWT-based login and password hashing using passlib.
* **Modular Architecture**: Organized into separate routers for scalability and clean code.
* **Data Ownership**: Full MySQL integration with Foreign Key relationships; every employee record is automatically linked to its owner to ensure data isolation.
* **Protected Endpoints**: All CRUD operations are locked behind authentication using FastAPI dependencies.
* **API Documentation**: Automatic, interactive Swagger UI documentation at /docs.

## 📁 Project Structure

├── main.py              # Entry point & Router registration
├── dependencies.py      # Security logic (get_current_user)
├── database.py          # MySQL Connection configuration
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic validation models
├── security.py          # Password hashing & JWT generation
└── routers/             # Modular endpoint definitions
    ├── auth.py          # User registration & login
    ├── products.py      # Product management
    ├── categories.py    # Category/Department management
    └── employees.py     # Employee personnel tracking

## 🛠️ Setup Instructions

### 1. Install Dependencies

Make sure you have your virtual environment activated, then run:
pip install -r requirements.txt

### 2. Configure Database

Update your MySQL credentials in database.py.

### 3. Run the API

uvicorn main:app --reload

---

## 🌐 API Endpoints

| Resource | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | POST | /login | Authenticate and obtain JWT |
| **Auth** | POST | /users/ | Register a new user account |
| **Products** | POST/GET | /products/ | Manage inventory items |
| **Categories** | POST/GET | /categories/ | Define departments |
| **Employees** | POST/GET | /employees/ | Manage staff (linked to owner) |

---

## 💡 Example Usage

**1. Authenticate (Get your Token)**
Use the /login endpoint to receive your access_token. You must provide this token in the header of all requests to protected routes.

**2. Creating an Employee (POST /employees/)**
*Request Body:*
{
  "name": "Alice Smith",
  "email": "<alice@example.com>",
  "category_id": 1
}

*Note: The server automatically assigns the owner_id based on your login token, ensuring data privacy.*
