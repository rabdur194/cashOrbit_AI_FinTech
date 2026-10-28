# Data model overview

The SQLAlchemy models are in `backend/app/models.py`; the exact fields and constraints in code are authoritative. Main concepts include:

- **Organization** — tenant boundary for business data.
- **User** — login identity, organization association, and role label.
- **Customer** — buyer/customer record belonging to an organization.
- **Invoice** — invoice number, customer, amount, due date, and balance/status fields.
- **Payment** — recorded amount and relationship to an invoice.
- **JournalEntry / JournalLine** — accounting event and debit/credit lines. Supported postings should balance.
- **BankTransaction** — imported statement row and reconciliation state.
- **AuditEvent** — record of selected actions. This is not tamper-proof storage.
- **Reminder/outbox record** — generated collection reminder; not proof of email delivery.
- **Portal token** — customer-scoped, expiring demo access token; raw token should be treated as a secret.
- **PaymentIntent / provider event** — gateway, invoice, amount, provider reference, and lifecycle state for sandbox checkout.
- **Financing simulation / offer** — illustrative calculation only.
- **Subscription/plan data** — simulated SaaS plan and usage.

## Money and accounting

Amounts should be represented in integer minor units. A production-grade implementation needs an explicit currency model, concurrency-safe payment posting, reversal/refund flows, taxes/credit notes, period controls, and independent accounting review.

## Tenant isolation

Organization IDs are used to scope core records. Before production, add automated tests for every route and object reference, including attempts to access another organization's invoice, payment, portal token, or payment intent.
