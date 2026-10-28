# Testing and verification

Do not equate a source-code compile or passing unit test with a working full-stack product. Run the checks below in a network-enabled environment and record any failures.

## Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

## Frontend

```bash
cd frontend
npm install
npm run typecheck
npm run build
```

## Docker smoke test

```bash
docker compose up --build
```

Check the UI at `http://localhost:3000`, `/health`, and `/docs`. Test login, create a customer, create an invoice, record a partial payment, and verify remaining balance and journal entries. Test CSV import with the provided sample file.

## Payment gateway checklist

Only use sandbox credentials. Verify: missing credentials show a clear error; checkout amount cannot exceed invoice balance; successful provider validation settles exactly once; callback/IPN replay does not duplicate ledger entries; failure/cancellation does not mark an invoice paid; mismatched amounts/references do not settle; a partial payment leaves the correct balance; ledger debits equal credits. Test delayed and duplicate notifications.

## Additional tests needed before production

- Cross-tenant access and object-level authorization tests.
- Role permission tests for every mutating route.
- Database transaction and concurrent callback/idempotency tests.
- Upload size/type/content validation and malformed CSV cases.
- Security checks for secrets, tokens, logs, CORS, rate limiting, CSRF/session strategy, and dependencies.
- Browser-based end-to-end tests and accessible responsive UI checks.
- Backup restore, monitoring, failure recovery, and provider settlement reconciliation.
