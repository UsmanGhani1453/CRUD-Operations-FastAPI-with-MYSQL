# FastAPI + MySQL Employee Management API

## 🚀 Features

* **Products:** Manage independent inventory items and pricing.
* **Categories:** Define department designations.
* **Employees:** Track staff information with a strict foreign-key relationship to Categories.

## 📁 Project Structure

* `main.py`: FastAPI routes and CRUD endpoints.
* `models.py`: SQLAlchemy database models defining the SQL tables.
* `schemas.py`: Pydantic schemas for data validation and API responses.
* `database.py`: MySQL database connection setup.

## 🛠️ Setup Instructions

### 1. Install Dependencies

Make sure you have your virtual environment activated, then run:

```bash

pip install -r requirements.txt
# ----------------------------------------------------------------------------------------
## 🌐 API Endpoints

Here is a summary of the available routes. 

### Products
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/products/` | Create a new product |
| **GET** | `/products/` | Get a list of all products |
| **GET** | `/products/{id}` | Get a specific product by ID |
| **PUT** | `/products/{id}` | Update an existing product |
| **DELETE** | `/products/{id}` | Delete a product |

### Categories
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/categories/` | Create a new department category |
| **GET** | `/categories/` | Get a list of all categories |
| **PUT** | `/categories/{id}` | Update an existing category |
| **DELETE** | `/categories/{id}` | Delete a category |

### Employees
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/employees/` | Register a new employee (requires valid `category_id`) |
| **GET** | `/employees/{id}` | Get specific employee details |
| **PUT** | `/employees/{id}` | Update employee information |
| **DELETE** | `/employees/{id}` | Remove an employee record |

---

## 💡 Example Usage

**Creating a new Employee (POST `/employees/`)**

*Request Body:*
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "category_id": 1
}
