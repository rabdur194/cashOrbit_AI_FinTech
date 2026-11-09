# CashOrbit

**B2B Receivables & Working-Capital Platform**  
Full-stack fintech portfolio project — invoice-to-cash, reconciliation, collections, and AI-assisted finance operations.
Forntend: https://cash-orbitaifintech-dlbt04316-rabdur194s-projects.vercel.app/
Backend: https://cashorbit-ai-fintech.onrender.com/health

![Stack](https://img.shields.io/badge/Next.js-15-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791) ![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6)

> **Portfolio project** — Built to demonstrate real fintech engineering patterns (double-entry ledger, bank reconciliation, multi-tenant data model, payment sandbox flows, and an AI finance assistant).  
> Not production financial software. Do not process real money or real customer data.

---

## Why this project exists

Many B2B businesses struggle with the same problems:

- Cash trapped in unpaid invoices (high DSO)
- Manual bank reconciliation
- Weak visibility into overdue receivables
- No clear audit trail of finance actions

CashOrbit implements the core **invoice → payment → ledger → reconciliation → collections** loop that real accounts-receivable platforms solve, with Bangladesh-relevant payment rails (bKash + SSLCOMMERZ sandbox) and an AI assistant on top.

---

## Live Demo (local)

| Service        | URL                          |
|----------------|------------------------------|
| Web App        | http://localhost:3000        |
| API Docs       | http://localhost:8000/docs   |
| Health Check   | http://localhost:8000/health |

**Demo login**  
Email: `demo@cashorbit.local`  
Password: `CashOrbitDemo123!`

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Frontend   | Next.js 15, React 19, TypeScript, Lucide icons  |
| Backend    | FastAPI, SQLAlchemy 2, Pydantic, JWT + Argon2   |
| Database   | PostgreSQL 16                                   |
| Infra      | Docker Compose, Alembic migrations scaffolding  |
| AI         | Optional OpenAI-compatible chat completions     |

---

## Core Features

### Finance Operations
- Customer & invoice management with status tracking
- Partial / full payment recording
- Automatic **double-entry journal entries** (AR ↔ Revenue, Cash ↔ AR)
- Dashboard KPIs: invoiced, collected, outstanding, overdue

### Reconciliation & Collections
- Bank statement CSV import (`reference,description,amount_minor,date`)
- Suggested matches + human confirmation
- Prioritized overdue collections queue
- Reminder outbox (simulated)

### Intelligence
- Receivables aging + 30/60/90-day cash forecast
- Simplified DSO proxy
- Rule-based anomaly detection with explanations
- **AI Finance Assistant** (organization-scoped, read-only, with deterministic fallback)

### Payments & Portal
- Sandbox checkout (internal)
- bKash + SSLCOMMERZ sandbox adapters
- Time-limited buyer portal tokens
- Financing simulation (illustrative only)

---

## Quick Start (Docker — recommended)

```bash
# 1. Clone / extract the project
cd CashOrbit

# 2. Create environment file
cp .env.example .env

# 3. Set a strong JWT secret (important)
# Edit .env and change JWT_SECRET to a long random string

# 4. Start everything
docker compose up --build
```

Open http://localhost:3000 and sign in with the demo account.

---

## Project Structure

```text
CashOrbit/
├── frontend/                 # Next.js 15 app (Vercel-ready)
│   ├── app/                  # App router pages
│   ├── components/           # Domain UI (dashboard, invoices, reconciliation…)
│   └── lib/                  # API client + types
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI routes
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── accounting.py     # Double-entry helpers
│   │   ├── security.py       # JWT + password hashing
│   │   └── routers/          # AI assistant router
│   ├── alembic/              # Migration scaffolding
│   └── tests/
├── docs/                     # Architecture, workflows, deployment
└── docker-compose.yml
```

---

## Deployment (Portfolio)

Recommended setup for showing recruiters:

| Component | Platform   | Why |
|-----------|------------|-----|
| Frontend  | **Vercel** | Perfect for Next.js |
| Backend   | **Railway** or **Render** | Easy Postgres + FastAPI |
| Database  | Railway Postgres / Neon | Managed, free hobby tier |

See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for step-by-step instructions.

---

## Architecture Highlights (for interviews)

- **Multi-tenant data model** — every business record is scoped by `organization_id`
- **Integer minor units** for money (avoids floating-point issues)
- **Double-entry ledger** on invoice issuance and payment receipt
- **Idempotent payment intents** + provider event tracking
- **Human-in-the-loop reconciliation** (never auto-posts matches)
- **Read-only AI assistant** with clear fallback when no API key is set
- Clean separation of frontend domain components

---

## Important Limitations

This is an **educational portfolio project**. It intentionally does **not** include:

- Live payment processing or real bank feeds
- Production-grade concurrent payment locking
- Real email/SMS delivery for reminders
- Full RBAC enforcement testing
- Certified accounting controls or regulatory compliance

Treat it as a demonstration of product thinking and engineering structure, not as software ready for real money.

---

## Local Development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

---

## License

No license is specified. Add one before public redistribution.

---

Built as a portfolio project to demonstrate full-stack fintech engineering.
