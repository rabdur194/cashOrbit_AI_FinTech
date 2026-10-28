# Learning guide: understand CashOrbit step by step

The goal is to understand the code, not only run the application. Read one workflow end to end, then make one small change and add a test.

## Stage 1 — Run and orient yourself
1. Start the Docker stack and open the UI and `/docs`.
2. Read `frontend/app/page.tsx` and `frontend/lib/api.ts` to see how UI actions call APIs.
3. Read `backend/app/main.py` to locate routes.
4. Trace login from browser to FastAPI, password verification, JWT creation, and protected endpoint.

## Stage 2 — Data and APIs
5. Follow customer creation: UI form → API request → Pydantic schema → SQLAlchemy model → database → response.
6. Follow invoice creation and inspect validation and invoice status/balance logic.
7. Add a field to a schema/model only after understanding migrations and database defaults.

## Stage 3 — Accounting
8. Trace invoice issuance into journal entries.
9. Record a partial payment and trace balance updates.
10. Verify the sum of debit lines equals the sum of credit lines. Add tests for overpayment, duplicate requests, and rounding.

## Stage 4 — Operational workflows
11. Import the sample statement and inspect reconciliation candidates.
12. Generate a reminder and distinguish an outbox record from a sent email.
13. Explain how aging buckets, DSO proxy, and due-date forecasts are calculated.
14. Trigger an anomaly and identify why a rule can produce false positives.

## Stage 5 — Payments
15. First use the simulated checkout; inspect the payment intent and event records.
16. Read `docs/PAYMENT_GATEWAYS.md`; configure sandbox credentials only if you have them.
17. Trace provider checkout creation, redirect, callback/IPN validation, settlement, ledger posting, and idempotency.
18. Test callback replay and failure/cancellation behavior. Never use real payment credentials for learning.

## Stage 6 — Quality and cloud
19. Run backend tests, frontend typecheck, and frontend build.
20. Add tenant-isolation tests and authorization tests before adding more features.
21. Read `docs/ARCHITECTURE.md` and `docs/AWS_DEPLOYMENT.md`; estimate costs before creating cloud resources.
22. Keep a short project journal explaining each change, the bug it solves, and how you verified it.

## Suggested interview explanations

Be ready to explain the problem, architecture, database schema, ledger balancing, reconciliation false positives, payment idempotency, provider-side validation, tenant isolation, security limitations, and which parts are sandboxed. Never claim live payment processing or production readiness unless it has actually been reviewed and verified.
