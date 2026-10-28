# API guide

The FastAPI interactive docs are at `http://localhost:8000/docs` after the app starts. Sign in using the demo UI or call `POST /auth/login`, then authorize requests with the returned bearer token. Swagger may automatically add the `Bearer` prefix; follow its prompt.

## Main endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/auth/login` | Obtain JWT |
| GET | `/auth/me` | Current user and organization |
| GET | `/dashboard/summary` | Dashboard metrics |
| GET/POST | `/customers` | List/create customers |
| GET/POST | `/invoices` | List/create invoices |
| POST | `/invoices/{id}/payments` | Record demo payment |
| GET | `/ledger` | Journal entries |
| POST | `/reconciliation/import-csv` | Import statement CSV |
| POST | `/reconciliation/confirm` | Confirm a suggested match |
| GET | `/reports/receivables.csv` | Export receivables |
| GET | `/collections/queue` | Prioritized unpaid invoices |
| POST | `/collections/run` | Generate reminder outbox records |
| GET | `/collections/reminders` | Reminder history |
| GET | `/analytics/working-capital` | Aging, DSO proxy, forecast |
| GET | `/analytics/anomalies` | Rule-based findings |
| POST | `/portal/invitations` | Create demo customer portal token |
| GET | `/portal/me?token=...` | Customer-scoped invoice view |
| GET | `/payments/providers/status` | Provider configuration status (no secrets) |
| POST | `/payments/providers/bkash/checkout` | Start bKash sandbox checkout |
| GET | `/payments/providers/bkash/callback` | bKash callback/verification |
| POST | `/payments/providers/sslcommerz/checkout` | Start SSLCOMMERZ hosted checkout |
| POST | `/payments/providers/sslcommerz/success` | Validate successful return |
| POST | `/payments/providers/sslcommerz/fail` | Handle failure return |
| POST | `/payments/providers/sslcommerz/cancel` | Handle cancellation return |
| POST | `/payments/providers/sslcommerz/ipn` | Validate asynchronous IPN |
| GET | `/payments/providers/intents` | List payment intents |
| POST | `/payments/sandbox/checkout` | Simulated offline checkout |
| GET | `/payments/sandbox/events` | Simulated provider events |
| POST | `/financing/simulate` | Simulate invoice advance |
| GET | `/financing/offers` | List simulations |
| GET | `/billing/subscription` | Read demo plan |
| POST | `/billing/change-plan` | Simulate plan change |
| GET | `/billing/usage` | Usage summary |
| GET/POST | `/team/users` | List/create team members |
| POST | `/portal/tokens/{id}/revoke` | Revoke portal token |
| GET | `/audit` | Recent audit events |

Endpoints may evolve as the project is extended. Swagger's live schema is the authoritative local view. Do not share raw buyer portal tokens or credentials.

## CSV format

Required headers: `reference,description,amount_minor,date`. Example: `BANK-DEMO-001,Customer payment,6500000,2026-10-21`. Amounts are integer minor units; for BDT, 100 paisa = 1 taka. See `backend/tests/sample_statement.csv`.


## AI assistant

- `POST /assistant/chat` — authenticated read-only finance assistant. Send `{ "messages": [{ "role": "user", "content": "Summarize overdue receivables" }] }`. The backend assembles invoice context for the authenticated organization only. With `OPENAI_API_KEY` configured, it calls the configured chat-completions model; without a key it returns a limited, explicitly labelled demo fallback. It never executes financial actions.
