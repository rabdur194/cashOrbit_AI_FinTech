# Contributing and local development

This is a learning-oriented codebase. Prefer small, reviewable changes with tests and documentation.

## Workflow
1. Create a branch for one change.
2. Explain the problem and expected behavior.
3. Add or update tests for business logic, authorization, and edge cases.
4. Run backend tests, frontend typecheck/build, and a local Docker smoke test where possible.
5. Update README or docs when behavior, setup, endpoints, or limitations change.
6. Never include `.env`, provider credentials, real financial data, database volumes, build outputs, or caches.

## Financial changes
Changes that affect invoice balances, payments, ledger entries, or payment callbacks need tests for idempotency, invalid amounts, partial payments, failures, duplicate callbacks, and debit/credit balance. Avoid silent financial state changes.

## Style
Keep business rules explicit and explainable. Validate API inputs, scope data to the authenticated organization, avoid logging secrets, and prefer migrations for schema changes.
