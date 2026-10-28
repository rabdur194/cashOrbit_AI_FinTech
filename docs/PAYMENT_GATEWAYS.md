# CashOrbit hosted payment gateways (sandbox)

CashOrbit supports two provider-hosted checkout adapters:

- **bKash Checkout** for bKash wallet payments.
- **SSLCOMMERZ Hosted Checkout** for the payment methods enabled for the merchant's SSLCOMMERZ account, including supported debit/credit cards such as Visa and Mastercard.

The project is sandbox-first. It does not collect card numbers, CVVs, expiry dates, or bKash PINs. Credentials belong only in the backend environment.

## Configuration

Set the following in `.env` and restart with `docker compose up --build`:

```dotenv
PAYMENT_PROVIDER_MODE=sandbox
PAYMENT_PUBLIC_BASE_URL=https://YOUR-PUBLIC-HTTPS-API.example
FRONTEND_PUBLIC_URL=http://localhost:3000
BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
BKASH_APP_KEY=
BKASH_APP_SECRET=
BKASH_USERNAME=
BKASH_PASSWORD=
SSLCOMMERZ_BASE_URL=https://sandbox.sslcommerz.com
SSLCOMMERZ_STORE_ID=
SSLCOMMERZ_STORE_PASSWORD=
```

Do not paste real credentials into source code, frontend environment variables, screenshots, or Git. `PAYMENT_PUBLIC_BASE_URL` must be reachable by the payment provider for callback/IPN delivery. For local development, use a trusted HTTPS tunnel and configure the provider's IPN URL as instructed by the provider. A provider server cannot call `localhost` on your laptop.

## Checkout lifecycle

1. The authenticated finance user opens an unpaid invoice and chooses a payment amount.
2. The browser asks CashOrbit's FastAPI backend to create a provider checkout. The server validates organization, invoice ownership, outstanding balance, currency, and provider amount limits.
3. The backend creates a `PaymentIntent`, then calls the provider with server-side credentials.
4. The customer is redirected to the provider-hosted sandbox payment page.
5. The provider returns the browser to the backend. bKash payment is executed server-side; SSLCOMMERZ callback/IPN transactions are validated with the provider's validation API.
6. Only after provider validation does CashOrbit mark the intent succeeded, record the payment, update invoice balances, post a balanced journal entry, and add an audit event. Duplicate success callbacks do not create a second payment.

## Test checklist

- Start with valid provider sandbox credentials.
- Confirm a checkout cannot be created without credentials.
- Test success, failure, and cancellation flows.
- Test a partial payment and confirm the remaining invoice balance is correct.
- Replay a callback and verify it does not post a second payment.
- Send an invalid/mismatched amount or transaction reference and verify the invoice remains unpaid or is marked for review.
- Confirm a successful payment produces balanced debit/credit journal lines.
- Verify a failed or cancelled checkout does not update the invoice or ledger.
- Test SSLCOMMERZ IPN delivery with a public HTTPS callback endpoint.

## Official documentation

- bKash sandbox merchant portal: <https://merchantdemo.sandbox.bka.sh/>
- bKash developer documentation: <https://developer.bka.sh/>
- SSLCOMMERZ v4 integration documentation: <https://developer.sslcommerz.com/doc/v4/index.html>
- SSLCOMMERZ sandbox registration: <https://developer.sslcommerz.com/registration/>

## Production is intentionally disabled

Do not switch these settings to production endpoints or use live credentials without a dedicated review. A production deployment needs provider approval, HTTPS, webhook/IPN operational monitoring, secure secret management, comprehensive concurrency and idempotency tests, refund/chargeback handling, settlement reconciliation, audit retention, security testing, and legal/regulatory review.
