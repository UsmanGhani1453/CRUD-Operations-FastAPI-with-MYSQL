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
- `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` — optional; if unset, checkout still works but skips payment (orders stay `unpaid`). See "Payments" below to enable real payments.

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

## Payments (Stripe)

Checkout creates a Stripe PaymentIntent when an order is placed and returns
its `client_secret` for the frontend to collect card details. **Payment
confirmation is handled by a webhook, not the browser** — a closed tab or
network blip on the client side can't fake a paid order.

1. Create a free Stripe account, stay in **test mode**.
2. Get your test secret key from https://dashboard.stripe.com/test/apikeys
   and set `STRIPE_SECRET_KEY` in `.env`.
3. For local development, install the [Stripe CLI](https://stripe.com/docs/stripe-cli)
   and run:
   ```bash
   stripe listen --forward-to localhost:8000/webhooks/stripe
   ```
   It prints a webhook signing secret (`whsec_...`) — put that in
   `STRIPE_WEBHOOK_SECRET`. Keep this command running alongside `uvicorn`
   while you test checkout locally; without it, `payment_intent.succeeded`
   events never reach your backend and orders stay `payment_status: unpaid`
   even after a successful card charge.
4. Test card number `4242 4242 4242 4242`, any future expiry, any CVC.
5. **Going live**: switch to live keys in the Stripe Dashboard, set
   `STRIPE_SECRET_KEY`/`STRIPE_WEBHOOK_SECRET` to the live versions, and
   add a webhook endpoint pointing at your deployed backend's
   `/webhooks/stripe` URL in the Stripe Dashboard (the CLI `listen` command
   is dev-only). No code changes needed.

If `STRIPE_SECRET_KEY` is left unset, orders still go through — they're
just marked `unpaid` and the frontend skips straight to the order
confirmation screen. Useful while you're still setting the rest of the app up.

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
| Webhooks | POST | `/webhooks/stripe` | Stripe only (signature-verified) |

## Security notes

- Passwords hashed with bcrypt via passlib; never stored or logged in plaintext.
- JWTs signed with `SECRET_KEY` from the environment — no static fallback in production.
- CORS origins configurable via `CORS_ALLOWED_ORIGINS`.
- Order creation uses `SELECT ... FOR UPDATE` on the product row to prevent
  race conditions from overselling stock.
