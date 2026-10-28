# Product roadmap and implementation status

CashOrbit includes a working portfolio-oriented vertical slice plus demo implementations for advanced workflows. “Implemented” means the application can execute the workflow using local/synthetic data; it does not mean production-grade financial approval or external provider connectivity.

## Included in this version

- Finance dashboard, customers, invoices, partial payments, basic double-entry ledger, audit events.
- CSV import, conservative match suggestions, reconciliation confirmation, receivables CSV export.
- Collections queue and simulated reminder outbox.
- Receivables aging, due-date cash-inflow baseline, DSO proxy.
- Explainable rule-based anomaly review.
- Time-limited, customer-scoped buyer portal tokens.
- Idempotency-key-aware simulated payment checkout and provider-event log.
- Invoice financing simulation with rationale and explicit disclaimer.
- Next.js UI for intelligence and operations, API docs, Docker local stack, AWS deployment guidance.

## Next engineering milestones

### Milestone 1 — verification and quality
- Install dependencies in a network-enabled development environment.
- Run backend unit/API tests, frontend typecheck/build, and browser-based smoke tests.
- Add tenant-isolation, authentication, authorization, upload-validation, duplicate webhook, and concurrency tests.
- Add CI that runs checks on every pull request.

### Milestone 2 — background jobs and communications
- Add a separately deployed worker that consumes reminder outbox jobs.
- Integrate an email provider in test mode, with delivery status, retries, exponential backoff, and dead-letter queue.
- Add scheduled jobs, customer statements, PDF receipts, and reminder preferences.

### Milestone 3 — financial correctness
- Replace simplistic matching with date/reference/amount/currency matching and confidence explanation.
- Add manual exceptions, split/combined payment support, reversals, refunds, credit notes, tax, currency and period controls.
- Add idempotency constraints and concurrency-safe payment posting.
- Add a reviewed chart of accounts and accounting domain review.

### Milestone 4 — data intelligence
- Store payment history and customer payment-delay features with consent and data minimization.
- Define labels and time-based train/validation/test splits.
- Evaluate anomaly detection and late-payment risk with precision/recall, calibration, false-positive analysis and monitoring.
- Keep model outputs explainable and require human review for consequential decisions.

### Milestone 5 — integration and cloud
- Implement real provider adapters only after approved provider sandbox credentials are available.
- Verify webhook signatures and replay/idempotency semantics per provider.
- Provision AWS via reviewed IaC, add secrets management, monitoring, backup/restore tests, deployment approvals and rollback.
- Conduct security, privacy, threat-model, legal and regulatory reviews before any real financial use.

### Milestone 6 — SaaS maturity
- Organization onboarding and invitations, verified email, secure session/refresh flow, MFA, granular role-based access control.
- Plans, entitlements, usage limits and subscription billing integration.
- Tenant export/deletion, retention policies, support tooling and immutable audit evidence where required.

## Non-goals of this demo

The project does not initiate real payments, access live bank accounts, send real emails, issue credit, make real underwriting decisions, or deploy AWS infrastructure automatically. Those are integrations and governance projects, not features that can be safely faked into a portfolio repository.
