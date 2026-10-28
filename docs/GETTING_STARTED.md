# Getting started

## Prerequisites
- Docker Desktop or Docker Engine with Docker Compose.
- VS Code or another editor.
- A modern browser.
- For manual checks: Python 3.12+ and Node.js 22 recommended.

## Start with Docker
1. Extract the package and open its root folder.
2. Copy `.env.example` to `.env`.
3. Replace the local `POSTGRES_PASSWORD` and `JWT_SECRET` values. Keep `.env` private.
4. Run `docker compose up --build`. The first build needs package-registry access.
5. Open `http://localhost:3000`, API docs at `http://localhost:8000/docs`, and health check at `http://localhost:8000/health`.
6. Use the local demo account `demo@cashorbit.local` / `CashOrbitDemo123!`. Change or remove demo credentials before any shared deployment.

## Stop and reset
- Stop containers: `docker compose down`.
- Reset local database and delete all demo data: `docker compose down -v`, then start again. This permanently removes the local database volume.

## Before payment testing
Do not expect real provider checkout to work until sandbox credentials are configured. Follow [Payment gateway setup](PAYMENT_GATEWAYS.md). Provider callback/IPN needs a publicly reachable HTTPS endpoint, often via a trusted development tunnel. Never use live credentials for local experimentation.
