# CashOrbit — B2B Receivables & Working-Capital SaaS

CashOrbit is a portfolio-grade full-stack fintech learning project for business invoicing, payment tracking, bank-statement reconciliation, collections workflows, working-capital indicators, explainable anomaly review, buyer access, payment-provider sandbox checkout, and financing simulation.

**Stack:** Next.js 15 + React + TypeScript · FastAPI · SQLAlchemy · PostgreSQL 16 · Docker Compose · Alembic scaffolding.

> **Scope and safety:** This is an educational portfolio application, not production financial software. bKash and SSLCOMMERZ support is intended for sandbox testing. Do not use live credentials or real customer data. Production use requires provider approval, security and accounting reviews, regulatory/legal review, robust tests, monitoring, operational controls, and verified end-to-end behavior.

## Start here

1. Install Docker Desktop or Docker Engine with Compose.
2. Extract this project and open the `CashOrbit-Complete` folder in VS Code.
3. Copy `.env.example` to `.env`.
4. Set a unique local `POSTGRES_PASSWORD` and long random `JWT_SECRET`. Keep `.env` private.
5. From the project root, run:

   ```bash
   docker compose up --build
   ```

6. Open the app and API docs:
   - Web app: <http://localhost:3000>
   - API docs: <http://localhost:8000/docs>
   - Health check: <http://localhost:8000/health>

**Demo account** (local learning only): `demo@cashorbit.local` / `CashOrbitDemo123!`

If startup fails, see [Troubleshooting](docs/TROUBLESHOOTING.md). This project has not been verified as a complete end-to-end deployment in every environment; follow [Testing and verification](docs/TESTING.md) before presenting it as fully tested.

## Feature overview

### Finance operations
- Dashboard summaries for invoiced, collected, outstanding, overdue, and reconciliation progress.
- Customer creation and directory.
- Invoice creation, due dates, invoice status, outstanding balances, duplicate invoice-number checks, and partial/full manual demo payment recording.
- Basic double-entry ledger for supported invoice and payment events; entries are expected to balance.
- Audit history for selected business operations.

### Reconciliation and collections
- Import bank-statement CSV files with the required headers `reference,description,amount_minor,date`.
- Skip duplicate external references, suggest conservative amount-based matches, and explicitly confirm matches.
- Export receivables as CSV.
- Prioritized unpaid/overdue invoice queue, generated reminder records, and reminder history. Reminder records are an outbox simulation; no email is sent by default.

### Intelligence and AI assistant
- Receivables aging, cumulative 30/60/90-day due-date inflow baseline, and a simplified DSO proxy.
- AI Finance Operations Assistant with organization-scoped invoice context, read-only answers, invoice references, and a clearly labelled demo fallback when no model key is configured.
- Optional OpenAI-compatible chat completions integration. Set `OPENAI_API_KEY` in `.env` and optionally `OPENAI_MODEL` to enable LLM-generated answers; the key is used by the backend only.
- The assistant does not execute payments, edit invoices, approve financing, or perform other financial actions. Treat generated explanations as assistance, not a financial control or audit substitute.
- Explainable rule-based anomaly findings for unusual amounts, repeated references, and unmatched transactions.
- These are transparent heuristics, not a trained AI model or a guarantee of future cash receipts.

### Customer portal and SaaS foundation
- Time-limited customer-scoped buyer portal tokens and token revocation endpoint.
- Basic team directory and role labels, organization-scoped core records, JWT demo authentication, and password hashing.
- Simulated SaaS plans and usage summaries; no subscription charge is made.

### Payment and financing demonstrations
- **bKash hosted Checkout sandbox** and **SSLCOMMERZ hosted checkout sandbox**. SSLCOMMERZ payment methods depend on merchant configuration and can include supported debit/credit cards such as Visa and Mastercard.
- Provider callbacks and server-side validation flows are represented in the backend; test with approved sandbox credentials and public HTTPS callback URLs.
- A separate simulated checkout for offline learning.
- Financing simulator with illustrative fees and rule-based explanation. It is not a real credit decision or loan offer.
- CashOrbit does not collect card numbers, CVVs, expiry dates, or bKash PINs. Payment credentials should be entered only on the provider-hosted page.

**Not included:** live payment processing, live bank feeds, real email delivery, actual lending, production AWS resources, certified accounting, or production compliance. See [Feature matrix](docs/FEATURE_MATRIX.md) and [Payment gateway setup](docs/PAYMENT_GATEWAYS.md).

## Documentation index

| Guide | What's inside |
|---|---|
| [Documentation index](docs/README.md) | How all project guides fit together |
| [Feature matrix](docs/FEATURE_MATRIX.md) | Implemented vs simulated vs not included |
| [Getting started](docs/GETTING_STARTED.md) | Local setup, prerequisites, first run |
| [Product workflows](docs/PRODUCT_WORKFLOWS.md) | Invoice-to-cash, reconciliation, collections, analytics, portal, sandbox |
| [Payment gateways](docs/PAYMENT_GATEWAYS.md) | bKash + SSLCOMMERZ setup and test checklist |
| [Architecture](docs/ARCHITECTURE.md) | Components and data flow |
| [Data model](docs/DATA_MODEL.md) | Main entities and relationships |
| [API guide](docs/API_GUIDE.md) | Main endpoints and how to explore Swagger |
| [Testing and verification](docs/TESTING.md) | Backend tests, frontend checks, payment test plan |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common Docker, environment, and callback issues |
| [Learning guide](docs/LEARNING_GUIDE.md) | Step-by-step coding curriculum |
| [AWS deployment direction](docs/AWS_DEPLOYMENT.md) | Cloud architecture guidance; no resources provisioned |
| [Roadmap](docs/ROADMAP.md) | Remaining engineering milestones |
| [Security policy](SECURITY.md) | Secrets, safe testing, and reporting concerns |
| [Contributing](CONTRIBUTING.md) | Local development conventions |
| [Changelog](CHANGELOG.md) | Package contents and notable changes |

## Project structure

```text
CashOrbit-Complete/
├── README.md                 # Start here
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── .env.example              # Example only; copy to .env
├── docker-compose.yml
├── .github/workflows/ci.yml
├── backend/
│   ├── app/                  # FastAPI routes, models, schemas, accounting, security, AI assistant router
│   ├── alembic/              # Migration configuration and versions
│   ├── tests/                # Backend test starter and sample statement CSV
│   ├── Dockerfile
│   └── requirements*.txt
├── frontend/
│   ├── app/                  # Next.js UI and styles
│   ├── lib/api.ts            # API client
│   ├── public/
│   └── Dockerfile
└── docs/                     # Product, technical, setup, and learning guides
```

## Environment configuration

The full list is in `.env.example`. Important variables:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: local database configuration.
- `DATABASE_URL`: SQLAlchemy connection string. In Docker Compose, the database hostname is `db`.
- `JWT_SECRET`: token signing secret; replace the example value.
- `CORS_ORIGINS`: allowed frontend origins.
- `NEXT_PUBLIC_API_URL`: API base URL used by the browser.
- `PAYMENT_PROVIDER_MODE`: keep set to `sandbox`.
- `PAYMENT_PUBLIC_BASE_URL`: public HTTPS API URL for provider callbacks/IPN; localhost cannot be reached by provider servers.
- `BKASH_*` and `SSLCOMMERZ_*`: backend-only sandbox credentials. Never expose them with `NEXT_PUBLIC_` prefixes.

See [Payment gateway setup](docs/PAYMENT_GATEWAYS.md) before testing providers. Never commit `.env` or real credentials.

## Quality checks

Backend:

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

Frontend (Node.js 22 recommended):

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

Run both sets of checks in a network-enabled environment and resolve failures before claiming a successful build. Also review [Testing and verification](docs/TESTING.md), particularly tenant-isolation and payment callback tests.

## Financial correctness and limitations

- Amounts are represented as integer minor units to avoid binary floating-point rounding.
- Invoice issuance and payment receipt have basic balanced journal posting.
- This is a small, simplified chart of accounts and single-currency learning model, not a complete accounting product.
- The application includes demo startup/seed behavior. Production should use controlled migrations and a separate seed process.
- Organization scoping and role foundations exist, but exhaustive object-level authorization testing is required.
- Reminder jobs are not sent by a production worker; anomaly detection and financing are rule-based; forecasts are simple estimates.
- Provider adapters require valid sandbox credentials and reachable callbacks to verify end to end. No real payment can be assumed to have succeeded without provider-side validation.
- Audit records are database rows, not immutable/tamper-proof evidence.

## License

No license is specified. Add a license before redistributing the code. Review third-party package and asset terms independently.
