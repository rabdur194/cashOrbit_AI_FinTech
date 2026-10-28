"use client";
import { Plus } from "lucide-react";
import type { Customer, Invoice, Page, Summary, Txn } from "../lib/types";
import { money } from "../lib/api";
import { Heading, initials } from "./ui";
import { Overview } from "./dashboard/Overview";
import { InvoiceTable } from "./invoices/InvoiceTable";
import { Reconciliation } from "./reconciliation/Reconciliation";
import { Ledger } from "./ledger/Ledger";
import { Audit } from "./audit/Audit";
import { AdvancedCenter } from "./operations/AdvancedCenter";
import { AssistantChat } from "./assistant/AssistantChat";

type Props = {
  page: Page; summary: Summary | null; invoices: Invoice[]; customers: Customer[]; txns: Txn[];
  ledger: any[]; audit: any[]; loading: boolean; error: string; notice: string; search: string;
  setSearch: (value: string) => void; setPage: (page: Page) => void;
  onNewInvoice: () => void; onNewCustomer: () => void; onPayment: (invoice: Invoice | null) => void;
  onRefresh: () => void; onImportCsv: (file: File) => Promise<any>; onConfirmMatch: (txn: Txn) => void;
};

export function WorkspaceContent(props: Props) {
  const {page,summary,invoices,customers,txns,ledger,audit,loading,error,notice,search,setSearch,setPage,onNewInvoice,onNewCustomer,onPayment,onRefresh,onImportCsv,onConfirmMatch}=props;
  const filtered=invoices.filter(i=>`${i.invoice_number} ${i.customer_name} ${i.status}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="main-content">{notice&&<div className="notice">{notice}</div>}{error&&<div className="notice error">{error}</div>}{loading&&<div style={{fontSize:11,color:"#8792a5",marginBottom:12}}>Refreshing workspace data…</div>}{page==="Overview"&&<Overview summary={summary} invoices={invoices} txns={txns} setPage={setPage} onNewInvoice={()=>onNewInvoice()} onRefresh={onRefresh}/ >}{page==="Invoices"&&<><Heading eyebrow="RECEIVABLES MANAGEMENT" title="Invoices" subtitle="Create, track and collect outstanding customer balances." action={<button className="button" onClick={()=>onNewInvoice()}><Plus size={15}/> New invoice</button>}/><div className="panel"><div className="panel-head"><div><h2>All invoices</h2><p>{invoices.length} invoices in this workspace</p></div><div className="toolbar"><input placeholder="Search invoices…" value={search} onChange={e=>setSearch(e.target.value)}/></div></div><InvoiceTable invoices={filtered} onPayment={onPayment}/></div></>}{page==="Customers"&&<><Heading eyebrow="CUSTOMER DIRECTORY" title="Customers" subtitle="Manage your business customers and their receivables." action={<button className="button" onClick={()=>onNewCustomer()}><Plus size={15}/> Add customer</button>}/><div className="panel"><div className="panel-head"><div><h2>Customer accounts</h2><p>{customers.length} customers</p></div></div><div className="table-wrap"><table><thead><tr><th>Customer</th><th>Email</th><th>Open invoices</th><th>Outstanding</th></tr></thead><tbody>{customers.map(c=>{const own=invoices.filter(i=>i.customer_id===c.id&&i.outstanding_minor>0);return <tr key={c.id}><td><div className="customer-cell"><div className="customer-icon">{initials(c.name)}</div><div><strong>{c.name}</strong><small>Customer ID #{c.id}</small></div></div></td><td>{c.email||"—"}</td><td>{own.length}</td><td className="amount">{money(own.reduce((a,i)=>a+i.outstanding_minor,0))}</td></tr>})}</tbody></table>{!customers.length&&<div className="empty">No customers yet. Add your first customer to get started.</div>}</div></div></>}{page==="Reconciliation"&&<Reconciliation txns={txns} onImport={async(file)=>onImportCsv(file)} onConfirm={(t)=>onConfirmMatch(t)}/ >}{page==="Ledger"&&<Ledger entries={ledger}/>}{page==="Intelligence"&&<AdvancedCenter mode="intelligence" invoices={invoices} customers={customers} onRefresh={onRefresh}/>}{page==="Operations"&&<AdvancedCenter mode="operations" invoices={invoices} customers={customers} onRefresh={onRefresh}/>}{page==="AI Assistant"&&<AssistantChat />} {page==="Audit trail"&&<Audit events={audit}/>}</div>;
}
