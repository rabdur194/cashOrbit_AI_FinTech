# Security policy

CashOrbit is an educational project. Do not use real customer, payment-card, wallet, or banking data. Do not expose it publicly with demo credentials.

## Secrets
- Copy `.env.example` to `.env`; never commit `.env`.
- Keep provider credentials on the backend only. Never use `NEXT_PUBLIC_` for secrets.
- Rotate any secret that has been committed, pasted into a ticket/chat, or shown in a screenshot. Deleting the visible copy alone may not revoke it.
- Keep payment provider mode set to sandbox.

## Payments
- Card numbers, CVVs, expiry dates, and bKash PINs must be entered only on the official provider-hosted page. CashOrbit must not collect them.
- Treat browser redirects as untrusted. Settle only after server-side provider validation and idempotent processing.
- Production use requires security, provider, accounting, legal/regulatory, and operational review.

## Reporting
Do not publish credentials, personal data, or exploit details in a public issue. For a private project, contact the repository owner directly with a concise description and safe reproduction steps.
