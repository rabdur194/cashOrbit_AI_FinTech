export type User = { id: number; name: string; email: string; role: string; organization_id: number; organization_name?: string };
export type Summary = { currency: string; invoice_count: number; total_invoiced_minor: number; collected_minor: number; outstanding_minor: number; overdue_count: number; overdue_minor: number; open_invoice_count: number; reconciliation_rate: number; recent_invoices: any[] };
export type Invoice = { id: number; invoice_number: string; customer_id: number; customer_name: string; description: string; amount_minor: number; paid_minor: number; outstanding_minor: number; currency: string; due_date: string; status: string };
export type Customer = { id: number; name: string; email: string };
export type Txn = { id: number; external_reference: string; description: string; amount_minor: number; transaction_date: string; matched_payment_id: number | null; match_status: string };
export type Page = "Overview" | "Invoices" | "Customers" | "Reconciliation" | "Ledger" | "Audit trail" | "Intelligence" | "Operations" | "AI Assistant";
