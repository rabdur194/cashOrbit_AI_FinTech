# Feature matrix

“Implemented” describes a portfolio workflow in this codebase, not production certification. Verify locally before relying on it.

| Feature | Status | Scope / limitation |
|---|---|---|
| Dashboard and finance summary | Implemented foundation | Synthetic/demo data supported |
| Customers and invoices | Implemented foundation | Basic validation and organization scoping |
| Manual payments | Implemented foundation | Demo/manual recording, partial payment checks |
| Double-entry ledger | Basic implementation | Supported events only; simplified chart of accounts |
| CSV bank-statement import | Implemented foundation | Required headers, duplicate-reference checks |
| Reconciliation | Implemented foundation | Conservative match suggestions and human confirmation |
| Collections queue | Implemented foundation | Prioritization and generated reminder records |
| Email reminders | Not live | No production mail delivery worker |
| Working-capital analytics | Basic heuristics | Aging, cumulative due-date forecast, DSO proxy |
| Anomaly review | Rule-based | Not trained AI and not proof of fraud |
| Buyer portal | Demo token flow | Security and UX hardening required |
| bKash checkout | Sandbox adapter | Requires provider sandbox credentials and reachable callback |
| SSLCOMMERZ cards/hosted checkout | Sandbox adapter | Available methods depend on merchant account; requires sandbox credentials |
| Payment callbacks/IPN | Code path included | Must be verified end-to-end with provider sandbox |
| Financing | Simulation only | No real underwriting, offer, or loan |
| SaaS plan / usage | Simulation only | No subscription charges |
| AWS | Documentation/configuration direction | No AWS resources provisioned |
| Production security/compliance | Not certified | Requires professional review and comprehensive tests |
