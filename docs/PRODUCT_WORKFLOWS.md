# CashOrbit workflow guide

## 1. Invoice to cash
1. Create or select a customer.
2. Create an invoice. The API validates customer organization ownership and duplicate invoice number.
3. Invoice issuance posts a balanced journal entry: debit accounts receivable, credit revenue.
4. Record a payment. The API checks that it does not exceed the remaining balance.
5. Payment receipt posts a balanced entry: debit cash/bank, credit accounts receivable.
6. The dashboard and invoice status reflect the updated balance.

## 2. Statement reconciliation
1. Prepare a CSV with `reference,description,amount_minor,date`.
2. Upload through the Reconciliation page or `POST /reconciliation/import-csv`.
3. Duplicate references are skipped; amount-only candidates may be marked `suggested`.
4. Review candidate transaction/payment details and explicitly confirm a match.
5. Inspect the audit trail for the confirmation.

Never treat amount-only matching as conclusive. Real implementations should use provider references, date windows, currencies, duplicate detection, confidence scores, and exception review.

## 3. Collections
1. `/collections/queue` returns open invoices sorted by overdue age and outstanding amount.
2. `POST /collections/run` creates reminder outbox records for overdue invoices, optionally including not-yet-due invoices.
3. `/collections/reminders` shows generated records.
4. No email is sent in this version. A production worker should claim jobs transactionally, send through a provider, record outcomes, retry transient errors, and dead-letter permanent failures.

## 4. Working-capital indicators
- Aging classifies open invoice balances by due-date age.
- The forecast sums balances due in the next 30, 60, and 90 days. The horizons are cumulative.
- DSO proxy is deliberately simplified. It should not be represented as a certified accounting metric.
- The anomaly endpoint provides transparent heuristic signals and explanations; it is not a trained AI system.

## 5. Payment sandbox
`POST /payments/sandbox/checkout` requires invoice ID, positive amount, provider label, and an idempotency key. It simulates success and records the event, payment, journal entry and audit event. Reusing the same key returns the existing event. No third-party provider is contacted and no funds move.

## 6. Buyer portal
Create a token with `POST /portal/invitations` and a customer ID. The response contains a one-time raw demo token. Call `GET /portal/me?token=...` to view only the invoices belonging to that customer and organization. Do not place real tokens in public links or logs. The token query-string design is for API demonstration; a production implementation should use a more secure session and delivery model.

## 7. Financing simulation
`POST /financing/simulate` accepts an invoice ID and requested advance in minor units. The API returns an illustrative fee, rule-based score, and rationale. It does not use credit bureau or bank data and must not be used to approve or decline a real borrower.
