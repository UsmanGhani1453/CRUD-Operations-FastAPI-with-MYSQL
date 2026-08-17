# FastAPI + MySQL CRUD API (HAAK)

A secure, modular RESTful API built with FastAPI, SQLAlchemy (MySQL), and JWT authentication. Covers products, categories, employees, users, and orders (with stock tracking).

## 🚀 Key Features

* **Secure Authentication** — JWT-based login, bcrypt password hashing via passlib.
* **Environment-driven config** — all secrets (DB URL, JWT secret, SMTP credentials) come from environment variables, never from source code. See `config.py` and `.env.example`.
* **Fail-fast in production** — missing required config (e.g. `SECRET_KEY`) raises at startup in production instead of silently falling back to an insecure default.
* **Role-based access control** — admin-only endpoints via `get_current_admin`; employee records are additionally scoped to their owning admin.
* **Inventory-safe orders** — order creation validates and decrements product stock inside the same transaction (with row locking) to prevent overselling under concurrent requests.
* **Modular architecture** — one router per resource.
* **Interactive docs** — Swagger UI at `/docs`, ReDoc at `/redoc`.

## 📁 Project Structure

```
.
├── main.py              # App entry point & router registration
├── config.py            # Centralized, env-driven configuration (fail-fast)
├── database.py          # SQLAlchemy engine/session setup
├── dependencies.py      # Auth dependencies (get_current_user / get_current_admin)
├── models.py            # SQLAlchemy ORM models
├── schemas.py            # Pydantic request/response models (with validation)
├── security.py          # Password hashing & JWT issuance
├── email_utils.py       # Verification email sending (SMTP)
├── seed.py               # Seeds an admin user, categories, and demo products
├── alembic/              # DB migrations (reads DATABASE_URL from env)
└── routers/
    ├── auth.py           # Login
    ├── users.py          # User creation (admin-only) & email verification
    ├── products.py        # Product CRUD
    ├── categories.py      # Category CRUD
    ├── employees.py        # Employee CRUD (owner-scoped)
    └── orders.py           # Order placement & status management
```

## 🛠️ Setup

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Then edit `.env` with real values. At minimum for local development you'll want:

- `DATABASE_URL` — your MySQL connection string
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `SENDER_EMAIL` / `SENDER_PASSWORD` — only needed if you want verification emails to actually send (use a Gmail **App Password**, never your real account password)

In development, missing values fall back to insecure defaults with a warning so you can get running quickly. **In production, set `ENVIRONMENT=production` and every required variable — the app will refuse to start otherwise.**

> ⚠️ **Never commit `.env` or hardcode credentials in source.** `.env` is already in `.gitignore`.

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. (Optional) Seed demo data

```bash
python seed.py
```

Creates an admin user (`SEED_ADMIN_EMAIL`, default `admin@haak.com`). If `SEED_ADMIN_PASSWORD` isn't set, a random one-time password is generated and printed — change it after first login.

### 5. Run the API

```bash
uvicorn main:app --reload
```

---

## 🌐 API Endpoints

| Resource | Method | Endpoint | Auth |
| :--- | :--- | :--- | :--- |
| Auth | POST | `/login` | — |
| Users | POST | `/users/` | Admin |
| Users | GET | `/users/verify?token=...` | — |
| Users | GET | `/users/me` | User |
| Products | POST/GET | `/products/` | Admin (POST) / User (GET) |
| Products | GET/PUT/DELETE | `/products/{id}` | User (GET) / Admin (PUT/DELETE) |
| Categories | POST/GET | `/categories/` | Admin (POST) / User (GET) |
| Categories | PUT/DELETE | `/categories/{id}` | Admin |
| Employees | POST | `/employees/` | Admin |
| Employees | GET | `/employees/search?key=&value=` | User |
| Employees | GET/PUT/DELETE | `/employees/{id}` | Owner-scoped |
| Orders | POST/GET | `/orders/` | User |
| Orders | GET | `/orders/all` | Admin |
| Orders | PUT | `/orders/{id}/status` | Admin |

---

## 🔒 Security notes

- Passwords are hashed with bcrypt via passlib; never stored or logged in plaintext.
- JWTs are signed with `SECRET_KEY` from the environment; there is no static fallback secret in production.
- CORS origins are configurable via `CORS_ALLOWED_ORIGINS` rather than hardcoded.
- Order creation uses `SELECT ... FOR UPDATE` on the product row to prevent race conditions from overselling stock.
