# HAAK — Full-Stack CRUD App

A leather-goods storefront + admin dashboard, built as two independently
deployable projects sharing one repo:

```
haak-app/
├── backend/     FastAPI + MySQL API (see backend/README.md)
└── frontend/    React (Vite) storefront + admin UI (see frontend/README.md)
```

Each has its own dependencies, its own `.env`, and its own README with
full setup instructions. This file just covers how they fit together.

## Quick start (local development)

**1. Backend** — in one terminal:

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then edit DATABASE_URL and SECRET_KEY
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

Runs on `http://127.0.0.1:8000`.

**2. Frontend** — in a second terminal:

```bash
cd frontend
npm install
cp .env.example .env.local  # VITE_API_URL should already point at :8000
npm run dev
```

Runs on `http://localhost:5173`.

**3. Connect them**: make sure the frontend's dev port is in the backend's
`CORS_ALLOWED_ORIGINS` (in `backend/.env`):

```
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Restart the backend after changing `.env`.

Then open `http://localhost:5173`, log in with the admin credentials
`seed.py` printed, and you're in.

## Why two top-level folders instead of one

Backend and frontend have different runtimes, dependency managers, and
lifecycles (you'll redeploy the frontend far more often than the backend
schema changes). Keeping them as siblings with their own README, `.env`,
and lockfile means either one can be handed to a different developer, put
in its own CI pipeline, or deployed to a different host without dragging
the other along.

## Where to look for what

| Question | See |
| :--- | :--- |
| How is the API organized? What's in `app/models` vs `app/schemas`? | `backend/README.md` |
| How do I add a new backend endpoint? | Add a route in `backend/app/api/routes/`, a schema in `backend/app/schemas/`, wire it into `backend/app/main.py` |
| How is the frontend organized? | `frontend/README.md` |
| How do I add a new page? | Add a component in `frontend/src/pages/`, register the route in `frontend/src/App.jsx` |
| How do I deploy this for real? | `frontend/README.md` → "Deploying" section |
