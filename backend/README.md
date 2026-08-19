# HAAK Backend — FastAPI + MySQL

A layered FastAPI application: products, categories, employees, users, and
orders (with real stock tracking), backed by MySQL via SQLAlchemy, with
JWT authentication.

## Project structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app instance, router registration
│   ├── core/
│   │   ├── config.py          # Env-driven settings (fail-fast in production)
│   │   └── security.py        # Password hashing, JWT issuance
│   ├── db/
│   │   └── session.py         # Engine, SessionLocal, Base, get_db
│   ├── models/                # One SQLAlchemy model per file
│   │   ├── user.py, category.py, product.py, employee.py, order.py
│   ├── schemas/                # One Pydantic schema module per resource
│   │   ├── user.py, category.py, product.py, employee.py, order.py
│   ├── api/
│   │   ├── deps.py             # get_current_user / get_current_admin
│   │   └── routes/             # One router per resource
│   │       ├── auth.py, users.py, products.py, categories.py,
│   │       └── employees.py, orders.py
│   └── services/
│       └── email.py            # SMTP verification email sending
├── alembic/                     # DB migrations
├── alembic.ini
├── seed.py                       # Seeds an admin user + demo catalog
├── requirements.txt
└── .env.example
```

This mirrors a standard layered-service layout: **routes** stay thin
(validate input, call the DB, return a schema), **models** own the schema
of the database, **schemas** own the shape of the API, and **core**/**db**
hold cross-cutting concerns so nothing in `api/` needs to know how the
database is wired up or where secrets come from.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- `DATABASE_URL` — your MySQL connection string
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `SENDER_EMAIL` / `SENDER_PASSWORD` — optional locally (use a Gmail **App Password**, never your real password)

In development, missing values fall back to insecure defaults with a
warning. **Set `ENVIRONMENT=production` and every required variable before
deploying — the app refuses to start otherwise.**

> ⚠️ Never commit `.env` or hardcode credentials in source. `.env` is
> already in `.gitignore`.

## Run migrations & seed data

```bash
alembic upgrade head
python seed.py
```

`seed.py` creates an admin user (`SEED_ADMIN_EMAIL`, default
`admin@haak.com`). If `SEED_ADMIN_PASSWORD` isn't set, a random one-time
password is generated and printed.

## Payments

There's no online payment provider. Orders are created with
`payment_status: unpaid`, and an admin marks them `paid` manually (e.g.
after a cash or bank transfer on delivery) via `PUT /orders/{id}/payment`
or the admin orders page in the frontend.

## Run the API

```bash
uvicorn app.main:app --reload
```

Note the module path is `app.main:app` (not `main:app`) — the app now
lives inside the `app/` package.

Docs at `http://127.0.0.1:8000/docs`.

## API endpoints

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
| Employees | POST/GET | `/employees/` | Admin |
| Employees | GET | `/employees/search?key=&value=` | User |
| Employees | GET/PUT/DELETE | `/employees/{id}` | Owner-scoped |
| Orders | POST/GET | `/orders/` | User |
| Orders | GET | `/orders/all` | Admin |
| Orders | GET | `/orders/{id}` | Owner or Admin |
| Orders | PUT | `/orders/{id}/status` | Admin |
| Orders | PUT | `/orders/{id}/payment` | Admin |

## Security notes

- Passwords hashed with bcrypt via passlib; never stored or logged in plaintext.
- JWTs signed with `SECRET_KEY` from the environment — no static fallback in production.
- CORS origins configurable via `CORS_ALLOWED_ORIGINS`.
- Order creation uses `SELECT ... FOR UPDATE` on the product row to prevent
  race conditions from overselling stock.
