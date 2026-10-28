"use client";
import { useEffect, useState } from "react";
import { api, clearToken, getToken, setToken } from "../lib/api";
import type { Customer, Invoice, Page, Summary, Txn, User } from "../lib/types";
import { Login } from "../components/auth/Login";
import { AppShell } from "../components/layout/AppShell";
import { WorkspaceContent } from "../components/WorkspaceContent";
import { CustomerModal, InvoiceModal, PaymentModal } from "../components/modals/FinanceModals";

export default function Home() {
  const [user,setUser]=useState<User|null>(null);
  const [page,setPage]=useState<Page>("Overview");
  const [summary,setSummary]=useState<Summary|null>(null);
  const [invoices,setInvoices]=useState<Invoice[]>([]);
  const [customers,setCustomers]=useState<Customer[]>([]);
  const [txns,setTxns]=useState<Txn[]>([]);
  const [ledger,setLedger]=useState<any[]>([]);
  const [audit,setAudit]=useState<any[]>([]);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState("");
  const [notice,setNotice]=useState("");
  const [showInvoice,setShowInvoice]=useState(false);
  const [showCustomer,setShowCustomer]=useState(false);
  const [showPayment,setShowPayment]=useState<Invoice|null>(null);
  const [search,setSearch]=useState("");

  useEffect(()=>{ if(getToken()) api<User>("/auth/me").then(setUser).catch(()=>setUser(null)); },[]);
  useEffect(()=>{
    const params=new URLSearchParams(window.location.search);
    const result=params.get("payment"); const provider=params.get("provider");
    if(result){
      const labels:Record<string,string>={succeeded:"Payment confirmed by the provider and recorded in the ledger.",pending:"Payment is pending provider confirmation.",failed:"Payment failed. The invoice remains unpaid.",cancelled:"Payment was cancelled. The invoice remains unpaid.",review_required:"Payment needs review. Check provider status before retrying.",unknown:"Payment return could not be matched to an invoice. Contact the finance administrator."};
      setNotice(`${provider||"Payment"}: ${labels[result]||`Payment status: ${result}`}`);
      window.history.replaceState({},"",window.location.pathname);
    }
  },[]);
  useEffect(()=>{ if(user) void loadAll(); },[user]);

  async function loadAll(){
    setLoading(true); setError("");
    try {
      const [s,i,c,t,l,a]=await Promise.all([api<Summary>("/dashboard/summary"),api<Invoice[]>("/invoices"),api<Customer[]>("/customers"),api<Txn[]>("/reconciliation/transactions"),api<any[]>("/ledger"),api<any[]>("/audit")]);
      setSummary(s);setInvoices(i);setCustomers(c);setTxns(t);setLedger(l);setAudit(a);
    } catch(e:unknown) { setError(e instanceof Error?e.message:"Unable to load data"); }
    finally { setLoading(false); }
  }
  async function login(email:string,password:string){
    setError("");
    try { const result=await api<any>("/auth/login",{method:"POST",body:JSON.stringify({email,password})});setToken(result.access_token);setUser(result.user); }
    catch(e:unknown){setError(e instanceof Error?e.message:"Login failed");}
  }
  function logout(){clearToken();setUser(null);setSummary(null);setPage("Overview");}
  async function act(fn:()=>Promise<any>,message:string){
    setError("");setNotice("");
    try { await fn();setNotice(message);await loadAll(); }
    catch(e:unknown){setError(e instanceof Error?e.message:"Action failed");throw e;}
  }
  if(!user) return <Login onLogin={login} error={error}/>;

  return <AppShell user={user} page={page} txns={txns} setPage={next=>{setPage(next);setNotice("");setError("");}} onLogout={logout} onRefresh={loadAll}>
    <WorkspaceContent page={page} summary={summary} invoices={invoices} customers={customers} txns={txns} ledger={ledger} audit={audit} loading={loading} error={error} notice={notice} search={search} setSearch={setSearch} setPage={setPage} onNewInvoice={()=>setShowInvoice(true)} onNewCustomer={()=>setShowCustomer(true)} onPayment={setShowPayment} onRefresh={loadAll}
      onImportCsv={async file=>{const form=new FormData();form.append("file",file);return act(()=>api("/reconciliation/import-csv",{method:"POST",body:form}),"CSV import complete. Review suggested matches below.");}}
      onConfirmMatch={txn=>{void act(()=>api("/reconciliation/confirm",{method:"POST",body:JSON.stringify({transaction_id:txn.id,payment_id:txn.matched_payment_id})}),"Reconciliation match confirmed.").catch(()=>{});}}
    />
    {showInvoice&&<InvoiceModal customers={customers} onClose={()=>setShowInvoice(false)} onSave={body=>act(()=>api("/invoices",{method:"POST",body:JSON.stringify(body)}),"Invoice created and journal entry posted.").then(()=>setShowInvoice(false))}/>}
    {showCustomer&&<CustomerModal onClose={()=>setShowCustomer(false)} onSave={body=>act(()=>api("/customers",{method:"POST",body:JSON.stringify(body)}),"Customer created.").then(()=>setShowCustomer(false))}/>}
    {showPayment&&<PaymentModal invoice={showPayment} onClose={()=>setShowPayment(null)} onSave={body=>act(()=>api(`/invoices/${showPayment.id}/payments`,{method:"POST",body:JSON.stringify(body)}),"Payment recorded and ledger updated.").then(()=>setShowPayment(null))} onCheckout={async(provider,amount_minor)=>{const result=await api<any>(`/payments/providers/${provider}/checkout`,{method:"POST",body:JSON.stringify({invoice_id:showPayment.id,amount_minor,provider,idempotency_key:`${provider}-${showPayment.id}-${Date.now()}-${Math.random().toString(36).slice(2,8)}`})});window.location.assign(result.redirect_url);}}/>}
  </AppShell>;
}
