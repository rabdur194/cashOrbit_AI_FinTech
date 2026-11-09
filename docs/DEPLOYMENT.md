# Deployment Guide — Portfolio Ready

This guide shows the simplest reliable way to deploy CashOrbit so you can share a live demo with recruiters.

**Recommended architecture**

```
Vercel (Frontend)  →  Railway / Render (FastAPI Backend)  →  Postgres
```

---

## 1. Backend + Database on Railway (easiest)

1. Create a free account at [railway.app](https://railway.app)
2. New Project → **Deploy from GitHub** (or upload the `backend` folder)
3. Add a **PostgreSQL** plugin to the same project
4. In the backend service, set these environment variables:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | (auto-filled by Railway Postgres plugin — use the `DATABASE_URL` they give you, change driver to `postgresql+psycopg://` if needed) |
| `JWT_SECRET` | Long random string (e.g. `openssl rand -hex 32`) |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` |
| `FRONTEND_PUBLIC_URL` | `https://your-frontend.vercel.app` |
| `PAYMENT_PUBLIC_BASE_URL` | `https://your-backend.up.railway.app` |
| `PAYMENT_PROVIDER_MODE` | `sandbox` |

5. Set the start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

6. Deploy. Copy the public backend URL (e.g. `https://cashorbit-api.up.railway.app`)

**Health check:** open `https://your-backend.../health` — should return `{"status":"ok"}`.

---

## 2. Frontend on Vercel

1. Create account at [vercel.com](https://vercel.com)
2. Import the repository (or the `frontend` folder)
3. Framework preset: **Next.js**
4. Set environment variable:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.up.railway.app` |

5. Deploy.

Your live app will be at `https://your-project.vercel.app`.

---

## 3. Alternative: Render

Same idea as Railway:

- Create a **Web Service** for the FastAPI backend
- Create a **PostgreSQL** instance
- Set the same environment variables
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 4. Local Docker (for development)

```bash
cp .env.example .env
# Edit JWT_SECRET
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000/docs

---

## 5. Checklist before sharing with recruiters

- [ ] Backend health endpoint works
- [ ] You can log in with the demo account
- [ ] Dashboard loads real sample data
- [ ] `CORS_ORIGINS` includes your Vercel domain
- [ ] README clearly states this is a **portfolio / educational** project
- [ ] No real payment credentials or customer data

---

## Demo Account

```
Email:    demo@cashorbit.local
Password: CashOrbitDemo123!
```

This account is automatically seeded on first startup.
