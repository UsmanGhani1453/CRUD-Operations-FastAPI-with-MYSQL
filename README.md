# FastAPI + MySQL Employee Management API

A robust REST API demonstrating relational database design and full CRUD operations using **FastAPI**, **SQLAlchemy**, and **MySQL**.

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
