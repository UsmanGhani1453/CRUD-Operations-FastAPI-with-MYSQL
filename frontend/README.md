# HAAK — React Storefront + Admin Dashboard

A React (Vite) frontend for the FastAPI + MySQL CRUD backend: a customer-facing
storefront with cart/checkout, plus an admin dashboard for managing products,
categories, employees, orders, and users.

Verified end-to-end against a live instance of the backend: login, product
listing, cart → checkout → order creation with real stock decrement, order
status updates, and CORS all confirmed working.

## Stack

- React 19 + Vite
- React Router v7
- Axios (with a request/response interceptor for auth + 401 handling)
- Plain CSS with design tokens (no UI framework) — see `src/styles/`

## Project structure

```
src/
├── api/
│   ├── client.js       # axios instance, token storage, error helper
│   └── resources.js    # one function per backend endpoint
├── context/
│   ├── AuthContext.jsx # login/logout, current user, role
│   └── CartContext.jsx # in-memory cart state
├── components/          # Navbar, CartDrawer, Modal, route guards, etc.
├── pages/
│   ├── Storefront.jsx, Login.jsx, Checkout.jsx, MyOrders.jsx
│   └── admin/            # AdminLayout + Products/Categories/Employees/Orders/Users
└── styles/               # design tokens + component styles
```

## 1. Point it at your backend

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```
VITE_API_URL=http://127.0.0.1:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

`VITE_API_URL` must be the full base URL of your running FastAPI backend
(no trailing slash).

`VITE_STRIPE_PUBLISHABLE_KEY` is your Stripe **publishable** key (safe to
expose in the browser — from the same Stripe account/mode as the backend's
`STRIPE_SECRET_KEY`). If you leave this out, checkout still works but the
payment step is skipped (matches the backend's behavior when Stripe isn't
configured there either).

## 2. Run locally

```bash
npm install
npm run dev
```

Opens on `http://localhost:5173` by default.

## 3. Backend requirements

The backend (in `../backend` if you got this as part of the monorepo) is
organized as a layered `app/` package — see its own README for the full
structure. It includes two additions made specifically to support this
frontend:

- `GET /employees/` — a list endpoint, scoped to the requesting admin's own
  employees.
- `role` on the `/users/me` response, so the frontend can tell admins from
  customers and show/hide the admin dashboard accordingly.

Run it with `uvicorn app.main:app --reload` (note the `app.main:app` module
path, not `main:app`).

Also make sure the backend's CORS is configured to allow this frontend's
origin — see `CORS_ALLOWED_ORIGINS` in the backend's `.env` (comma-separated
list, no wildcards with credentials enabled).

## 4. How auth works here

- `POST /login` expects `application/x-www-form-urlencoded` (OAuth2 password
  form) — handled for you in `src/api/resources.js`.
- The JWT is stored in `localStorage` and attached to every request via an
  axios interceptor.
- A `401` response from any endpoint clears the token and the app falls back
  to the logged-out state automatically (see `auth-expired` event in
  `client.js` / `AuthContext.jsx`).
- New accounts are created by an admin via **Admin → Users** (`POST /users/`)
  — there's no public self-registration page, matching the backend's design.
- Promoting a user to admin has no API route by design (see backend review);
  do it directly in the database (`UPDATE users SET role='admin' WHERE ...`).

## 5. Build for production

```bash
npm run build
```

Outputs static files to `dist/`. Preview locally with `npm run preview`.

## 6. Deploying ("going live")

This is a static site once built — deploy `dist/` to any static host.

**Vercel / Netlify (recommended, zero-config for Vite):**
1. Push this project to a Git repo.
2. Import it in Vercel or Netlify. Both auto-detect Vite
   (build command `npm run build`, output directory `dist`).
3. Set the environment variable `VITE_API_URL` in the platform's dashboard to
   your deployed backend's public URL. Redeploy after setting it — Vite bakes
   env vars in at build time, not runtime.

**Backend side, once the frontend has a real domain:**
1. Deploy the FastAPI backend somewhere that can reach your MySQL database
   (Railway, Render, Fly.io, a VPS, etc.) — see the backend's own README.
2. Set `CORS_ALLOWED_ORIGINS` on the backend to your frontend's real domain,
   e.g. `https://haak.vercel.app` (no trailing slash, exact origin).
3. Set `ENVIRONMENT=production` on the backend so it fails fast on any
   missing required secret instead of silently using an insecure default.
4. Re-point the frontend's `VITE_API_URL` at the backend's real HTTPS URL
   and redeploy the frontend.

Both frontend and backend need to be HTTPS in production for cookies/auth
headers to behave consistently across browsers — most hosts (Vercel,
Netlify, Railway, Render) give you this by default.

## Known limitations / next steps

- No public self-registration; admins create accounts.
- No password-reset flow.
- No pagination on the storefront or admin tables (fine at current scale;
  the backend supports `skip`/`limit` if you need it later).
- Product images aren't modeled on the backend yet — the storefront shows a
  placeholder tile per product. Add an `image_url` field to `Product` /
  `ProductCreate` on the backend to wire in real photography.
