from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
import csv, io, json, secrets, hashlib, statistics
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import httpx, uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from .config import settings
from .database import Base, engine, get_db, SessionLocal
from . import models, schemas
from .security import hash_password, verify_password, create_access_token, get_current_user
from .accounting import post_journal, audit
from .routers.assistant import router as assistant_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    yield

app = FastAPI(title="CashOrbit API", version="0.1.0", description="Learning MVP for B2B receivables, reconciliation and working-capital insights", lifespan=lifespan)
origins = [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(assistant_router)

def seed_demo_data():
    db = SessionLocal()
    try:
        user = db.scalar(select(models.User).where(models.User.email == "demo@cashorbit.local"))
        if user: return
        org = models.Organization(name="Northstar Trading Ltd")
        db.add(org); db.flush()
        user = models.User(organization_id=org.id, email="demo@cashorbit.local", full_name="Demo Finance Owner", password_hash=hash_password("CashOrbitDemo123!"), role="owner")
        db.add(user); db.flush()
        c1 = models.Customer(organization_id=org.id, name="Meghna Supplies", email="accounts@meghna.example")
        c2 = models.Customer(organization_id=org.id, name="Eastern Retail Group", email="finance@eastern.example")
        db.add_all([c1,c2]); db.flush()
        inv1 = models.Invoice(organization_id=org.id, customer_id=c1.id, invoice_number="CO-2026-001", description="Wholesale inventory", amount_minor=18500000, paid_minor=6500000, currency="BDT", due_date="2026-11-05", status="partially_paid")
        inv2 = models.Invoice(organization_id=org.id, customer_id=c2.id, invoice_number="CO-2026-002", description="Monthly supply order", amount_minor=9200000, paid_minor=0, currency="BDT", due_date="2026-10-18", status="overdue")
        inv3 = models.Invoice(organization_id=org.id, customer_id=c1.id, invoice_number="CO-2026-003", description="Logistics and handling", amount_minor=4700000, paid_minor=4700000, currency="BDT", due_date="2026-10-22", status="paid")
        db.add_all([inv1,inv2,inv3]); db.flush()
        p1 = models.Payment(organization_id=org.id, invoice_id=inv1.id, amount_minor=6500000, reference="BK-DEMO-0001", method="bank_transfer", status="succeeded")
        p2 = models.Payment(organization_id=org.id, invoice_id=inv3.id, amount_minor=4700000, reference="BK-DEMO-0002", method="bank_transfer", status="succeeded")
        db.add_all([p1,p2]); db.flush()
        post_journal(db,user,"invoice",inv1.id,"Invoice issued CO-2026-001",[{"account_code":"1100","account_name":"Accounts receivable","debit_minor":18500000},{"account_code":"4000","account_name":"Sales revenue","credit_minor":18500000}])
        post_journal(db,user,"payment",p1.id,"Payment received BK-DEMO-0001",[{"account_code":"1000","account_name":"Cash and bank","debit_minor":6500000},{"account_code":"1100","account_name":"Accounts receivable","credit_minor":6500000}])
        post_journal(db,user,"invoice",inv2.id,"Invoice issued CO-2026-002",[{"account_code":"1100","account_name":"Accounts receivable","debit_minor":9200000},{"account_code":"4000","account_name":"Sales revenue","credit_minor":9200000}])
        post_journal(db,user,"invoice",inv3.id,"Invoice issued CO-2026-003",[{"account_code":"1100","account_name":"Accounts receivable","debit_minor":4700000},{"account_code":"4000","account_name":"Sales revenue","credit_minor":4700000}])
        post_journal(db,user,"payment",p2.id,"Payment received BK-DEMO-0002",[{"account_code":"1000","account_name":"Cash and bank","debit_minor":4700000},{"account_code":"1100","account_name":"Accounts receivable","credit_minor":4700000}])
        db.add(models.BankTransaction(organization_id=org.id, external_reference="BANK-DEMO-001", description="Meghna payment BK-DEMO-0001", amount_minor=6500000, transaction_date="2026-10-21", matched_payment_id=p1.id, match_status="matched"))
        db.add(models.BankTransaction(organization_id=org.id, external_reference="BANK-DEMO-002", description="Unknown incoming transfer", amount_minor=1250000, transaction_date="2026-10-23", match_status="unmatched"))
        db.commit()
    except Exception:
        db.rollback(); raise
    finally: db.close()

@app.get("/health")
def health(): return {"status":"ok","service":"cashorbit-api"}

@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == payload.email.lower().strip()))
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(user), "user":{"id":user.id,"name":user.full_name,"email":user.email,"role":user.role,"organization_id":user.organization_id}}

@app.get("/auth/me")
def me(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.get(models.Organization, user.organization_id)
    return {"id":user.id,"name":user.full_name,"email":user.email,"role":user.role,"organization_id":user.organization_id,"organization_name":org.name if org else ""}

@app.get("/dashboard/summary")
def dashboard(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoices = list(db.scalars(select(models.Invoice).where(models.Invoice.organization_id == user.organization_id)))
    total = sum(x.amount_minor for x in invoices)
    paid = sum(x.paid_minor for x in invoices)
    today = date.today().isoformat()
    overdue = [x for x in invoices if x.due_date < today and x.paid_minor < x.amount_minor]
    open_invoices = [x for x in invoices if x.paid_minor < x.amount_minor]
    txns = list(db.scalars(select(models.BankTransaction).where(models.BankTransaction.organization_id == user.organization_id)))
    return {"currency":"BDT","invoice_count":len(invoices),"total_invoiced_minor":total,"collected_minor":paid,"outstanding_minor":total-paid,"overdue_count":len(overdue),"overdue_minor":sum(x.amount_minor-x.paid_minor for x in overdue),"open_invoice_count":len(open_invoices),"reconciliation_rate":round(100*sum(t.match_status=="matched" for t in txns)/len(txns)) if txns else 100,"recent_invoices":[invoice_dict(x, db) for x in sorted(invoices,key=lambda a:a.id,reverse=True)[:5]]}

def invoice_dict(inv, db):
    customer = db.get(models.Customer, inv.customer_id)
    return {"id":inv.id,"invoice_number":inv.invoice_number,"customer_id":inv.customer_id,"customer_name":customer.name if customer else "Unknown","description":inv.description,"amount_minor":inv.amount_minor,"paid_minor":inv.paid_minor,"outstanding_minor":inv.amount_minor-inv.paid_minor,"currency":inv.currency,"due_date":inv.due_date,"status":inv.status,"created_at":inv.created_at.isoformat()}

@app.get("/customers")
def list_customers(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(models.Customer).where(models.Customer.organization_id==user.organization_id).order_by(models.Customer.name)).all()
    return [{"id":x.id,"name":x.name,"email":x.email} for x in items]

@app.post("/customers")
def create_customer(payload: schemas.CustomerCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    item=models.Customer(organization_id=user.organization_id,name=payload.name.strip(),email=payload.email.strip())
    db.add(item); db.flush(); audit(db,user,"customer.created","customer",item.id,{"name":item.name}); db.commit(); db.refresh(item)
    return {"id":item.id,"name":item.name,"email":item.email}

@app.get("/invoices")
def list_invoices(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items=db.scalars(select(models.Invoice).where(models.Invoice.organization_id==user.organization_id).order_by(models.Invoice.id.desc())).all()
    return [invoice_dict(x,db) for x in items]

@app.post("/invoices")
def create_invoice(payload: schemas.InvoiceCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer=db.scalar(select(models.Customer).where(models.Customer.id==payload.customer_id,models.Customer.organization_id==user.organization_id))
    if not customer: raise HTTPException(status_code=404,detail="Customer not found in your organization")
    if db.scalar(select(models.Invoice).where(models.Invoice.organization_id==user.organization_id,models.Invoice.invoice_number==payload.invoice_number)):
        raise HTTPException(status_code=409,detail="Invoice number already exists")
    try:
        inv=models.Invoice(organization_id=user.organization_id,customer_id=customer.id,invoice_number=payload.invoice_number,description=payload.description,amount_minor=payload.amount_minor,currency=payload.currency.upper(),due_date=payload.due_date,status="issued")
        db.add(inv); db.flush()
        post_journal(db,user,"invoice",inv.id,f"Invoice issued {inv.invoice_number}",[{"account_code":"1100","account_name":"Accounts receivable","debit_minor":inv.amount_minor},{"account_code":"4000","account_name":"Sales revenue","credit_minor":inv.amount_minor}])
        audit(db,user,"invoice.created","invoice",inv.id,{"invoice_number":inv.invoice_number}); db.commit(); db.refresh(inv)
        return invoice_dict(inv,db)
    except Exception:
        db.rollback(); raise

@app.post("/invoices/{invoice_id}/payments")
def record_payment(invoice_id: int, payload: schemas.PaymentCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv=db.scalar(select(models.Invoice).where(models.Invoice.id==invoice_id,models.Invoice.organization_id==user.organization_id))
    if not inv: raise HTTPException(status_code=404,detail="Invoice not found")
    remaining=inv.amount_minor-inv.paid_minor
    if payload.amount_minor>remaining: raise HTTPException(status_code=400,detail="Payment exceeds invoice outstanding balance")
    try:
        p=models.Payment(organization_id=user.organization_id,invoice_id=inv.id,amount_minor=payload.amount_minor,reference=payload.reference,method=payload.method,status="succeeded")
        db.add(p); db.flush(); inv.paid_minor += payload.amount_minor
        inv.status="paid" if inv.paid_minor==inv.amount_minor else "partially_paid"
        post_journal(db,user,"payment",p.id,f"Payment received for {inv.invoice_number}",[{"account_code":"1000","account_name":"Cash and bank","debit_minor":p.amount_minor},{"account_code":"1100","account_name":"Accounts receivable","credit_minor":p.amount_minor}])
        audit(db,user,"payment.recorded","payment",p.id,{"invoice_id":inv.id,"amount_minor":p.amount_minor}); db.commit(); db.refresh(inv)
        return {"payment_id":p.id,"invoice":invoice_dict(inv,db),"message":"Payment recorded"}
    except Exception:
        db.rollback(); raise

@app.get("/ledger")
def list_ledger(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries=db.scalars(select(models.JournalEntry).options(joinedload(models.JournalEntry.lines)).where(models.JournalEntry.organization_id==user.organization_id).order_by(models.JournalEntry.id.desc())).unique().all()
    out=[]
    for e in entries:
        out.append({"id":e.id,"reference_type":e.reference_type,"reference_id":e.reference_id,"memo":e.memo,"created_at":e.created_at.isoformat(),"lines":[{"account_code":l.account_code,"account_name":l.account_name,"debit_minor":l.debit_minor,"credit_minor":l.credit_minor} for l in e.lines]})
    return out

@app.get("/reconciliation/transactions")
def list_transactions(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items=db.scalars(select(models.BankTransaction).where(models.BankTransaction.organization_id==user.organization_id).order_by(models.BankTransaction.id.desc())).all()
    return [{"id":x.id,"external_reference":x.external_reference,"description":x.description,"amount_minor":x.amount_minor,"transaction_date":x.transaction_date,"matched_payment_id":x.matched_payment_id,"match_status":x.match_status} for x in items]

@app.post("/reconciliation/import-csv")
async def import_csv(file: UploadFile = File(...), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(status_code=400,detail="Upload a CSV file")
    raw=await file.read()
    if len(raw)>2_000_000: raise HTTPException(status_code=413,detail="CSV must be smaller than 2 MB")
    try: rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    except Exception: raise HTTPException(status_code=400,detail="Could not read CSV")
    required={"reference","description","amount_minor","date"}
    if not rows or not required.issubset(set(rows[0].keys())): raise HTTPException(status_code=400,detail="CSV headers must be reference,description,amount_minor,date")
    created=0; duplicates=0
    try:
        for row in rows:
            ref=row["reference"].strip()
            if not ref: continue
            exists=db.scalar(select(models.BankTransaction).where(models.BankTransaction.organization_id==user.organization_id,models.BankTransaction.external_reference==ref))
            if exists: duplicates+=1; continue
            amount=int(row["amount_minor"])
            if amount<=0: continue
            txn=models.BankTransaction(organization_id=user.organization_id,external_reference=ref,description=row["description"].strip(),amount_minor=amount,transaction_date=row["date"].strip(),match_status="unmatched")
            db.add(txn); db.flush(); created+=1
            candidates=db.scalars(select(models.Payment).where(models.Payment.organization_id==user.organization_id,models.Payment.amount_minor==amount,models.Payment.status=="succeeded")).all()
            if len(candidates)==1:
                txn.matched_payment_id=candidates[0].id; txn.match_status="suggested"
        audit(db,user,"reconciliation.csv_imported","bank_transactions",None,{"created":created,"duplicates":duplicates}); db.commit()
    except Exception:
        db.rollback(); raise
    return {"created":created,"duplicates_skipped":duplicates,"message":"Import complete. Suggested matches must be reviewed."}

@app.post("/reconciliation/confirm")
def confirm_match(payload: schemas.ReconcileRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    txn=db.scalar(select(models.BankTransaction).where(models.BankTransaction.id==payload.transaction_id,models.BankTransaction.organization_id==user.organization_id))
    payment=db.scalar(select(models.Payment).where(models.Payment.id==payload.payment_id,models.Payment.organization_id==user.organization_id))
    if not txn or not payment: raise HTTPException(status_code=404,detail="Transaction or payment not found")
    if txn.amount_minor!=payment.amount_minor: raise HTTPException(status_code=400,detail="Amounts do not match; manual exception handling is required")
    if txn.match_status=="matched": raise HTTPException(status_code=409,detail="Transaction already matched")
    txn.matched_payment_id=payment.id; txn.match_status="matched"; audit(db,user,"reconciliation.match_confirmed","bank_transaction",txn.id,{"payment_id":payment.id}); db.commit()
    return {"message":"Match confirmed","transaction_id":txn.id,"payment_id":payment.id}

@app.get("/audit")
def audit_events(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    items=db.scalars(select(models.AuditEvent).where(models.AuditEvent.organization_id==user.organization_id).order_by(models.AuditEvent.id.desc()).limit(100)).all()
    return [{"id":x.id,"action":x.action,"entity_type":x.entity_type,"entity_id":x.entity_id,"details":x.details,"created_at":x.created_at.isoformat()} for x in items]


# ---------------- Advanced portfolio modules ----------------
# These endpoints intentionally use sandbox/demo behavior. They do not send real
# emails, initiate payments, connect to banks, or make regulated lending decisions.
from pydantic import BaseModel, Field

class ReminderRequest(BaseModel):
    invoice_id: int | None = None
    include_not_due: bool = False

class SandboxPaymentRequest(BaseModel):
    invoice_id: int
    amount_minor: int = Field(gt=0)
    provider: str = "cashorbit-sandbox"
    idempotency_key: str = Field(min_length=8, max_length=120)

class FinancingRequest(BaseModel):
    invoice_id: int
    requested_minor: int = Field(gt=0)

class PortalRequest(BaseModel):
    customer_id: int

@app.get("/analytics/working-capital")
def working_capital(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoices = list(db.scalars(select(models.Invoice).where(models.Invoice.organization_id == user.organization_id)).all())
    today = date.today()
    outstanding = [i for i in invoices if i.amount_minor > i.paid_minor]
    def days_past_due(i):
        try: return max(0, (today - date.fromisoformat(i.due_date)).days)
        except ValueError: return 0
    aging = {"current":0,"1_30_days":0,"31_60_days":0,"61_90_days":0,"90_plus_days":0}
    for inv in outstanding:
        days=days_past_due(inv); amount=inv.amount_minor-inv.paid_minor
        key="current" if days==0 else "1_30_days" if days<=30 else "31_60_days" if days<=60 else "61_90_days" if days<=90 else "90_plus_days"
        aging[key]+=amount
    # Transparent baseline forecast: all outstanding invoices are assigned to their due-date bucket.
    forecast=[]
    for horizon in (30,60,90):
        total=0
        for inv in outstanding:
            try: due=date.fromisoformat(inv.due_date)
            except ValueError: continue
            if today <= due <= today+timedelta(days=horizon): total += inv.amount_minor-inv.paid_minor
        forecast.append({"days":horizon,"expected_inflow_minor":total,"method":"outstanding invoice due-date baseline; no payment probability model"})
    total_paid=sum(i.paid_minor for i in invoices); total_invoiced=sum(i.amount_minor for i in invoices)
    return {"currency":"BDT","outstanding_minor":sum(i.amount_minor-i.paid_minor for i in outstanding),"overdue_minor":sum((i.amount_minor-i.paid_minor) for i in outstanding if days_past_due(i)>0),"invoice_count":len(invoices),"aging_minor":aging,"forecast":forecast,"dso_proxy_days":round((sum(i.amount_minor-i.paid_minor for i in outstanding)/total_invoiced)*90,1) if total_invoiced else 0,"method_note":"Portfolio demonstration only. DSO proxy and due-date forecast are simplified indicators, not accounting advice."}

@app.get("/analytics/anomalies")
def anomaly_scan(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    payments=list(db.scalars(select(models.Payment).where(models.Payment.organization_id==user.organization_id)).all())
    invoices=list(db.scalars(select(models.Invoice).where(models.Invoice.organization_id==user.organization_id)).all())
    findings=[]
    amounts=[p.amount_minor for p in payments]
    median=statistics.median(amounts) if amounts else 0
    for p in payments:
        reasons=[]; score=0
        if amounts and median and p.amount_minor >= median*3: reasons.append("Payment is at least 3x the portfolio median"); score+=35
        dup=db.scalars(select(models.Payment).where(models.Payment.organization_id==user.organization_id,models.Payment.reference==p.reference,models.Payment.id!=p.id)).all() if p.reference else []
        if dup: reasons.append("Payment reference appears more than once"); score+=70
        inv=next((i for i in invoices if i.id==p.invoice_id),None)
        if inv and p.amount_minor > inv.amount_minor: reasons.append("Payment exceeds original invoice amount"); score+=80
        if reasons: findings.append({"type":"payment_review","payment_id":p.id,"invoice_id":p.invoice_id,"amount_minor":p.amount_minor,"score":min(score,100),"severity":"high" if score>=70 else "medium","reasons":reasons,"automated_action":False})
    txns=list(db.scalars(select(models.BankTransaction).where(models.BankTransaction.organization_id==user.organization_id,models.BankTransaction.match_status=="unmatched")).all())
    for t in txns:
        findings.append({"type":"unmatched_bank_transaction","transaction_id":t.id,"amount_minor":t.amount_minor,"score":45,"severity":"medium","reasons":["Bank transaction has not been reconciled"],"automated_action":False})
    return {"count":len(findings),"findings":findings,"method":"Explainable rules and robust median baseline; not a trained AI model. Review alerts manually."}

@app.get("/collections/queue")
def collection_queue(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    today=date.today().isoformat()
    invoices=db.scalars(select(models.Invoice).where(models.Invoice.organization_id==user.organization_id,models.Invoice.paid_minor<models.Invoice.amount_minor)).all()
    out=[]
    for inv in invoices:
        customer=db.get(models.Customer,inv.customer_id)
        days=0
        try: days=max(0,(date.today()-date.fromisoformat(inv.due_date)).days)
        except ValueError: pass
        out.append({"invoice_id":inv.id,"invoice_number":inv.invoice_number,"customer":customer.name if customer else "Unknown","email":customer.email if customer else "","due_date":inv.due_date,"outstanding_minor":inv.amount_minor-inv.paid_minor,"days_overdue":days,"priority":"urgent" if days>30 else "high" if days>0 else "normal","suggested_action":"Escalate to finance owner" if days>30 else "Send overdue reminder" if days>0 else "Friendly due-date reminder"})
    return sorted(out,key=lambda x:(-x["days_overdue"],-x["outstanding_minor"]))

@app.post("/collections/run")
def run_collection_reminders(payload: ReminderRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    queue=collection_queue(user,db); created=[]
    for item in queue:
        if payload.invoice_id and item["invoice_id"]!=payload.invoice_id: continue
        if item["days_overdue"]==0 and not payload.include_not_due: continue
        inv=db.get(models.Invoice,item["invoice_id"])
        job=models.ReminderJob(organization_id=user.organization_id,invoice_id=inv.id,recipient=item["email"],subject=f"Payment reminder: {inv.invoice_number}",body=f"Demo reminder for {inv.invoice_number}. Outstanding amount: {item['outstanding_minor']} minor units. Please review your account statement.",status="simulated")
        db.add(job); db.flush(); created.append({"id":job.id,"invoice_id":inv.id,"recipient":job.recipient,"subject":job.subject,"status":"simulated_not_sent"})
    audit(db,user,"collections.reminders_generated","reminder_job",None,{"count":len(created)}); db.commit()
    return {"created":len(created),"items":created,"notice":"Reminder jobs were generated for demo purposes; no email was sent."}

@app.get("/collections/reminders")
def list_reminders(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    jobs=db.scalars(select(models.ReminderJob).where(models.ReminderJob.organization_id==user.organization_id).order_by(models.ReminderJob.id.desc()).limit(100)).all()
    return [{"id":j.id,"invoice_id":j.invoice_id,"recipient":j.recipient,"subject":j.subject,"body":j.body,"status":j.status,"created_at":j.created_at.isoformat()} for j in jobs]

@app.post("/portal/invitations")
def create_portal_invitation(payload: PortalRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    customer=db.scalar(select(models.Customer).where(models.Customer.id==payload.customer_id,models.Customer.organization_id==user.organization_id))
    if not customer: raise HTTPException(status_code=404,detail="Customer not found")
    raw=secrets.token_urlsafe(32); digest=hashlib.sha256(raw.encode()).hexdigest()
    item=models.PortalToken(organization_id=user.organization_id,customer_id=customer.id,token_hash=digest,expires_at=datetime.now(timezone.utc)+timedelta(days=7))
    db.add(item); audit(db,user,"portal.invitation_created","portal_token",None,{"customer_id":customer.id}); db.commit()
    return {"customer_id":customer.id,"customer_name":customer.name,"portal_token":raw,"expires_at":item.expires_at.isoformat(),"warning":"Demo bearer link. Deliver only through a secure channel; token is shown once. This is not a production invitation flow."}

@app.get("/portal/me")
def buyer_portal(token: str, db: Session = Depends(get_db)):
    digest=hashlib.sha256(token.encode()).hexdigest()
    access=db.scalar(select(models.PortalToken).where(models.PortalToken.token_hash==digest,models.PortalToken.revoked==False))
    if not access or access.expires_at.replace(tzinfo=timezone.utc)<datetime.now(timezone.utc): raise HTTPException(status_code=401,detail="Portal link is invalid or expired")
    customer=db.get(models.Customer,access.customer_id)
    invoices=db.scalars(select(models.Invoice).where(models.Invoice.organization_id==access.organization_id,models.Invoice.customer_id==access.customer_id).order_by(models.Invoice.id.desc())).all()
    return {"customer":{"name":customer.name if customer else "Unknown","email":customer.email if customer else ""},"invoices":[{"invoice_number":i.invoice_number,"description":i.description,"amount_minor":i.amount_minor,"paid_minor":i.paid_minor,"outstanding_minor":i.amount_minor-i.paid_minor,"currency":i.currency,"due_date":i.due_date,"status":i.status} for i in invoices]}

@app.post("/payments/sandbox/checkout")
def sandbox_checkout(payload: SandboxPaymentRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing=db.scalar(select(models.ProviderEvent).where(models.ProviderEvent.organization_id==user.organization_id,models.ProviderEvent.event_key==payload.idempotency_key))
    if existing: return {"event_id":existing.id,"status":existing.status,"message":"Idempotent replay: event already exists"}
    inv=db.scalar(select(models.Invoice).where(models.Invoice.id==payload.invoice_id,models.Invoice.organization_id==user.organization_id))
    if not inv: raise HTTPException(status_code=404,detail="Invoice not found")
    if payload.amount_minor>inv.amount_minor-inv.paid_minor: raise HTTPException(status_code=400,detail="Amount exceeds invoice outstanding balance")
    event=models.ProviderEvent(organization_id=user.organization_id,provider=payload.provider,event_key=payload.idempotency_key,event_type="checkout.succeeded",payload=json.dumps({"invoice_id":inv.id,"amount_minor":payload.amount_minor,"provider":payload.provider}),status="simulated")
    db.add(event); db.flush()
    p=models.Payment(organization_id=user.organization_id,invoice_id=inv.id,amount_minor=payload.amount_minor,reference=f"SANDBOX-{event.id}",method=payload.provider,status="succeeded")
    db.add(p); db.flush(); inv.paid_minor+=payload.amount_minor; inv.status="paid" if inv.paid_minor==inv.amount_minor else "partially_paid"
    post_journal(db,user,"payment",p.id,f"Sandbox payment for {inv.invoice_number}",[{"account_code":"1000","account_name":"Cash and bank (sandbox)","debit_minor":p.amount_minor},{"account_code":"1100","account_name":"Accounts receivable","credit_minor":p.amount_minor}])
    audit(db,user,"payment.sandbox_succeeded","provider_event",event.id,{"invoice_id":inv.id,"payment_id":p.id}); db.commit()
    return {"event_id":event.id,"payment_id":p.id,"status":"simulated_success","provider":payload.provider,"message":"Sandbox only. No external payment was initiated."}

@app.get("/payments/sandbox/events")
def sandbox_events(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    events=db.scalars(select(models.ProviderEvent).where(models.ProviderEvent.organization_id==user.organization_id).order_by(models.ProviderEvent.id.desc()).limit(100)).all()
    return [{"id":e.id,"provider":e.provider,"event_key":e.event_key,"event_type":e.event_type,"payload":json.loads(e.payload),"status":e.status,"created_at":e.created_at.isoformat()} for e in events]

# ---------------- bKash + SSLCOMMERZ hosted checkout integrations ----------------
# These routes call official provider sandbox APIs when credentials are configured.
# They never accept raw card data. The hosted provider page collects sensitive credentials.

def _provider_ready(provider: str):
    if provider == "bkash":
        ready = all([settings.bkash_app_key, settings.bkash_app_secret, settings.bkash_username, settings.bkash_password])
        if not ready:
            raise HTTPException(status_code=503, detail="bKash sandbox credentials are missing. Configure BKASH_APP_KEY, BKASH_APP_SECRET, BKASH_USERNAME, and BKASH_PASSWORD in .env.")
    elif provider == "sslcommerz":
        if not settings.sslcommerz_store_id or not settings.sslcommerz_store_password:
            raise HTTPException(status_code=503, detail="SSLCOMMERZ sandbox credentials are missing. Configure SSLCOMMERZ_STORE_ID and SSLCOMMERZ_STORE_PASSWORD in .env.")
    if settings.payment_provider_mode.lower() != "sandbox":
        raise HTTPException(status_code=400, detail="This project only enables sandbox mode by default. Review and explicitly harden any production deployment first.")

def _complete_provider_intent(db, intent, provider_txn_id: str, reference: str):
    # Idempotent settlement: one successful provider intent can create only one payment.
    if intent.status == "succeeded":
        return False
    inv = db.scalar(select(models.Invoice).where(models.Invoice.id == intent.invoice_id, models.Invoice.organization_id == intent.organization_id))
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice for payment intent not found")
    remaining = inv.amount_minor - inv.paid_minor
    if intent.amount_minor <= 0 or intent.amount_minor > remaining:
        intent.status = "review_required"
        intent.raw_status = "amount_or_balance_mismatch"
        db.commit()
        raise HTTPException(status_code=409, detail="Payment amount no longer matches the invoice balance; manual review required")
    p = models.Payment(organization_id=intent.organization_id, invoice_id=inv.id, amount_minor=intent.amount_minor,
                       reference=(reference or provider_txn_id or intent.merchant_reference)[:100], method=intent.provider, status="succeeded")
    db.add(p); db.flush()
    inv.paid_minor += intent.amount_minor
    inv.status = "paid" if inv.paid_minor == inv.amount_minor else "partially_paid"
    # Resolve the initiating user for the audit event if still available.
    actor = db.get(models.User, intent.created_by_user_id) if intent.created_by_user_id else db.scalar(select(models.User).where(models.User.organization_id == intent.organization_id).order_by(models.User.id))
    if actor:
        post_journal(db, actor, "payment", p.id, f"{intent.provider.upper()} payment for {inv.invoice_number}", [
            {"account_code":"1000","account_name":"Cash and bank - provider settlement","debit_minor":p.amount_minor},
            {"account_code":"1100","account_name":"Accounts receivable","credit_minor":p.amount_minor}])
        audit(db, actor, "payment.provider_succeeded", "payment_intent", intent.id, {"provider":intent.provider,"payment_id":p.id,"provider_transaction_id":provider_txn_id})
    intent.provider_transaction_id = (provider_txn_id or "")[:120]
    intent.status = "succeeded"
    intent.raw_status = "VALID"
    db.commit()
    return True

@app.get("/payments/providers/status")
def payment_provider_status(user: models.User = Depends(get_current_user)):
    return {
        "mode": "sandbox",
        "bkash": {"configured": bool(settings.bkash_app_key and settings.bkash_app_secret and settings.bkash_username and settings.bkash_password), "label":"bKash Checkout"},
        "sslcommerz": {"configured": bool(settings.sslcommerz_store_id and settings.sslcommerz_store_password), "label":"SSLCOMMERZ cards and local payment channels"},
        "note":"Provider hosted checkout is sandbox-only. Credentials are server-side and never returned."}

@app.post("/payments/providers/{provider}/checkout")
async def provider_checkout(provider: str, payload: SandboxPaymentRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    provider = provider.lower().strip()
    if provider not in {"bkash", "sslcommerz"}:
        raise HTTPException(status_code=400, detail="Supported providers: bkash, sslcommerz")
    _provider_ready(provider)
    inv = db.scalar(select(models.Invoice).where(models.Invoice.id == payload.invoice_id, models.Invoice.organization_id == user.organization_id))
    if not inv: raise HTTPException(status_code=404, detail="Invoice not found")
    if payload.amount_minor > inv.amount_minor - inv.paid_minor: raise HTTPException(status_code=400, detail="Amount exceeds invoice outstanding balance")
    if inv.currency.upper() != "BDT": raise HTTPException(status_code=400, detail="These Bangladesh payment gateways require BDT invoices in this integration")
    amount = payload.amount_minor / 100
    if provider == "sslcommerz" and not (10 <= amount <= 500000):
        raise HTTPException(status_code=400, detail="SSLCOMMERZ supports transaction amounts from BDT 10.00 to BDT 500,000.00 in this integration")
    intent = models.PaymentIntent(organization_id=user.organization_id, invoice_id=inv.id, created_by_user_id=user.id, provider=provider, amount_minor=payload.amount_minor,
                                  currency="BDT", merchant_reference=f"CO-{provider[:3].upper()}-{uuid.uuid4().hex[:20].upper()}", status="initiating")
    db.add(intent); db.commit(); db.refresh(intent)
    base = settings.payment_public_base_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            if provider == "bkash":
                token_url = settings.bkash_base_url.rstrip("/") + "/tokenized/checkout/token/grant"
                token_resp = await client.post(token_url, json={"app_key":settings.bkash_app_key,"app_secret":settings.bkash_app_secret}, headers={
                    "username":settings.bkash_username,"password":settings.bkash_password,"X-APP-Key":settings.bkash_app_key,"Content-Type":"application/json","Accept":"application/json"})
                token_resp.raise_for_status(); token_data = token_resp.json()
                id_token = token_data.get("id_token")
                if not id_token: raise HTTPException(status_code=502, detail="bKash did not return an access token; verify sandbox credentials and base URL")
                create_resp = await client.post(settings.bkash_base_url.rstrip("/") + "/tokenized/checkout/create", json={
                    "mode":"0011","payerReference":str(inv.id),"callbackURL":base+"/payments/providers/bkash/callback",
                    "amount":f"{amount:.2f}","currency":"BDT","intent":"sale","merchantInvoiceNumber":intent.merchant_reference
                }, headers={"Authorization":id_token,"X-APP-Key":settings.bkash_app_key,"Content-Type":"application/json","Accept":"application/json"})
                create_resp.raise_for_status(); data=create_resp.json()
                if data.get("statusCode") not in (None, "0000") or not data.get("bkashURL"):
                    raise HTTPException(status_code=502, detail="bKash checkout creation failed: " + str(data.get("statusMessage") or data.get("statusCode") or "unknown provider response"))
                intent.provider_payment_id = str(data.get("paymentID") or "")
                intent.redirect_url = str(data["bkashURL"])
            else:
                customer = db.get(models.Customer, inv.customer_id)
                form = {
                    "store_id":settings.sslcommerz_store_id,"store_passwd":settings.sslcommerz_store_password,
                    "total_amount":f"{amount:.2f}","currency":"BDT","tran_id":intent.merchant_reference,
                    "success_url":base+"/payments/providers/sslcommerz/success","fail_url":base+"/payments/providers/sslcommerz/fail",
                    "cancel_url":base+"/payments/providers/sslcommerz/cancel","ipn_url":base+"/payments/providers/sslcommerz/ipn",
                    "cus_name":(customer.name if customer else "CashOrbit Customer")[:50],
                    "cus_email":((customer.email if customer and customer.email else "customer@example.com")[:50]),
                    "cus_add1":"Dhaka","cus_city":"Dhaka","cus_state":"Dhaka","cus_postcode":"1207","cus_country":"Bangladesh",
                    "cus_phone":"01700000000","shipping_method":"NO","num_of_item":"1","product_name":f"Invoice {inv.invoice_number}"[:255],
                    "product_category":"business service","product_profile":"non-physical-goods","value_a":str(user.organization_id),"value_b":str(inv.id)
                }
                response = await client.post(settings.sslcommerz_base_url.rstrip("/")+"/gwprocess/v4/api.php", data=form)
                response.raise_for_status(); data=response.json()
                redirect_url = data.get("GatewayPageURL") or data.get("redirectGatewayURL")
                if data.get("status") != "SUCCESS" or not redirect_url:
                    raise HTTPException(status_code=502, detail="SSLCOMMERZ session creation failed: " + str(data.get("failedreason") or "unknown provider response"))
                intent.provider_payment_id = str(data.get("sessionkey") or "")
                intent.redirect_url = str(redirect_url)
        intent.status="pending"
        db.commit()
        return {"intent_id":intent.id,"provider":provider,"status":"pending","redirect_url":intent.redirect_url,
                "merchant_reference":intent.merchant_reference,"message":"Redirect the customer to the provider-hosted sandbox checkout."}
    except HTTPException:
        intent.status="initiation_failed"; db.commit(); raise
    except (httpx.HTTPError, ValueError) as exc:
        intent.status="initiation_failed"; intent.raw_status=type(exc).__name__; db.commit()
        raise HTTPException(status_code=502, detail=f"Could not start {provider} sandbox checkout. Check credentials, provider sandbox access, and network connectivity.")

@app.get("/payments/providers/bkash/callback")
async def bkash_callback(paymentID: str = "", status: str = "", db: Session = Depends(get_db)):
    if not paymentID:
        return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=failed&provider=bkash", status_code=303)
    intent = db.scalar(select(models.PaymentIntent).where(models.PaymentIntent.provider=="bkash",models.PaymentIntent.provider_payment_id==paymentID))
    if not intent:
        return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=unknown&provider=bkash", status_code=303)
    if intent.status == "succeeded":
        return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=succeeded&provider=bkash", status_code=303)
    if status.lower() == "success":
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                token_resp=await client.post(settings.bkash_base_url.rstrip("/")+"/tokenized/checkout/token/grant",json={"app_key":settings.bkash_app_key,"app_secret":settings.bkash_app_secret},headers={"username":settings.bkash_username,"password":settings.bkash_password,"X-APP-Key":settings.bkash_app_key,"Content-Type":"application/json","Accept":"application/json"})
                token_resp.raise_for_status(); token=token_resp.json().get("id_token")
                if not token: raise ValueError("Missing bKash token")
                execute=await client.post(settings.bkash_base_url.rstrip("/")+"/tokenized/checkout/execute",json={"paymentID":paymentID},headers={"Authorization":token,"X-APP-Key":settings.bkash_app_key,"Content-Type":"application/json","Accept":"application/json"})
                execute.raise_for_status(); data=execute.json()
            try: executed_minor = round(float(data.get("amount") or 0) * 100)
            except (ValueError, TypeError): executed_minor = -1
            invoice_reference = str(data.get("merchantInvoiceNumber") or intent.merchant_reference)
            if (data.get("transactionStatus")=="Completed" and data.get("trxID")
                    and executed_minor == intent.amount_minor and invoice_reference == intent.merchant_reference):
                _complete_provider_intent(db,intent,str(data.get("trxID")),invoice_reference)
            else:
                intent.status="failed"; intent.raw_status=str(data.get("transactionStatus") or data.get("statusMessage") or "failed")[:80]; db.commit()
        except Exception:
            intent.status="review_required"; intent.raw_status="execute_or_validation_error"; db.commit()
            return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=review&provider=bkash", status_code=303)
    else:
        intent.status="cancelled" if status.lower()=="cancel" else "failed"; intent.raw_status=status[:80]; db.commit()
    return RedirectResponse(settings.frontend_public_url.rstrip("/")+f"/?payment={intent.status}&provider=bkash", status_code=303)

async def _validate_sslcommerz_transaction(val_id: str):
    if not val_id: return None
    async with httpx.AsyncClient(timeout=25.0) as client:
        response=await client.get(settings.sslcommerz_base_url.rstrip("/")+"/validator/api/validationserverAPI.php",params={
            "val_id":val_id,"store_id":settings.sslcommerz_store_id,"store_passwd":settings.sslcommerz_store_password,"v":"1","format":"json"})
        response.raise_for_status(); return response.json()

async def _process_sslcommerz_status(form_data: dict, db: Session):
    tran_id=str(form_data.get("tran_id") or "")
    intent=db.scalar(select(models.PaymentIntent).where(models.PaymentIntent.provider=="sslcommerz",models.PaymentIntent.merchant_reference==tran_id))
    if not intent: return "unknown"
    val_id=str(form_data.get("val_id") or "")
    if not val_id: return intent.status
    validated=await _validate_sslcommerz_transaction(val_id)
    if not validated: return intent.status
    valid_status=str(validated.get("status") or "").upper()
    try: paid_minor=round(float(validated.get("amount") or 0)*100)
    except (ValueError,TypeError): paid_minor=-1
    if valid_status in {"VALID","VALIDATED"} and paid_minor==intent.amount_minor and str(validated.get("tran_id") or "")==intent.merchant_reference:
        _complete_provider_intent(db,intent,str(validated.get("bank_tran_id") or val_id),intent.merchant_reference)
    elif valid_status in {"FAILED","CANCELLED","INVALID_TRANSACTION"}:
        intent.status="failed" if valid_status!="CANCELLED" else "cancelled"; intent.raw_status=valid_status; db.commit()
    else:
        intent.status="review_required"; intent.raw_status=valid_status[:80]; db.commit()
    return intent.status

@app.post("/payments/providers/sslcommerz/success")
async def sslcommerz_success(request: Request, db: Session = Depends(get_db)):
    data=dict(await request.form())
    try: status=await _process_sslcommerz_status(data,db)
    except Exception: status="review_required"
    return RedirectResponse(settings.frontend_public_url.rstrip("/")+f"/?payment={status}&provider=sslcommerz",status_code=303)

@app.post("/payments/providers/sslcommerz/fail")
async def sslcommerz_fail(request: Request, db: Session = Depends(get_db)):
    data=dict(await request.form()); tran_id=str(data.get("tran_id") or "")
    intent=db.scalar(select(models.PaymentIntent).where(models.PaymentIntent.provider=="sslcommerz",models.PaymentIntent.merchant_reference==tran_id))
    if intent and intent.status not in {"succeeded"}: intent.status="failed"; intent.raw_status="provider_fail_callback"; db.commit()
    return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=failed&provider=sslcommerz",status_code=303)

@app.post("/payments/providers/sslcommerz/cancel")
async def sslcommerz_cancel(request: Request, db: Session = Depends(get_db)):
    data=dict(await request.form()); tran_id=str(data.get("tran_id") or "")
    intent=db.scalar(select(models.PaymentIntent).where(models.PaymentIntent.provider=="sslcommerz",models.PaymentIntent.merchant_reference==tran_id))
    if intent and intent.status not in {"succeeded"}: intent.status="cancelled"; intent.raw_status="provider_cancel_callback"; db.commit()
    return RedirectResponse(settings.frontend_public_url.rstrip("/")+"/?payment=cancelled&provider=sslcommerz",status_code=303)

@app.post("/payments/providers/sslcommerz/ipn")
async def sslcommerz_ipn(request: Request, db: Session = Depends(get_db)):
    data=dict(await request.form())
    try: status=await _process_sslcommerz_status(data,db)
    except Exception: raise HTTPException(status_code=502,detail="Payment validation temporarily failed; provider may retry the IPN")
    return {"received":True,"status":status}

@app.get("/payments/providers/intents")
def list_provider_intents(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows=db.scalars(select(models.PaymentIntent).where(models.PaymentIntent.organization_id==user.organization_id).order_by(models.PaymentIntent.id.desc()).limit(100)).all()
    return [{"id":x.id,"invoice_id":x.invoice_id,"provider":x.provider,"amount_minor":x.amount_minor,"merchant_reference":x.merchant_reference,"provider_transaction_id":x.provider_transaction_id,"status":x.status,"raw_status":x.raw_status,"created_at":x.created_at.isoformat()} for x in rows]

@app.post("/financing/simulate")
def simulate_financing(payload: FinancingRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv=db.scalar(select(models.Invoice).where(models.Invoice.id==payload.invoice_id,models.Invoice.organization_id==user.organization_id))
    if not inv: raise HTTPException(status_code=404,detail="Invoice not found")
    customer=db.get(models.Customer,inv.customer_id); remaining=inv.amount_minor-inv.paid_minor
    if payload.requested_minor>remaining: raise HTTPException(status_code=400,detail="Requested amount exceeds invoice outstanding balance")
    age=0
    try: age=max(0,(date.today()-date.fromisoformat(inv.due_date)).days)
    except ValueError: pass
    score=min(100,20+(30 if age>30 else 15 if age>0 else 0)+(25 if payload.requested_minor>remaining*.8 else 0)+(25 if not customer or not customer.email else 0))
    rationale=["Uses invoice balance and days past due only","No credit bureau, bank data, or real underwriting is used"]
    if age>30: rationale.append("Invoice is more than 30 days overdue")
    if payload.requested_minor>remaining*.8: rationale.append("Requested advance exceeds 80% of the outstanding invoice")
    offer=models.FinancingOffer(organization_id=user.organization_id,customer_id=inv.customer_id,invoice_id=inv.id,requested_minor=payload.requested_minor,risk_score=score,indicative_fee_bps=250,status="simulated_review" if score<60 else "simulated_high_risk",rationale="; ".join(rationale))
    db.add(offer); db.flush(); audit(db,user,"financing.simulated","financing_offer",offer.id,{"score":score}); db.commit()
    return {"offer_id":offer.id,"invoice_id":inv.id,"requested_minor":payload.requested_minor,"indicative_fee_bps":offer.indicative_fee_bps,"indicative_fee_minor":round(payload.requested_minor*offer.indicative_fee_bps/10000),"risk_score":score,"status":offer.status,"rationale":rationale,"disclaimer":"Educational simulation only, not a lending decision or offer of credit."}

@app.get("/financing/offers")
def financing_offers(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    offers=db.scalars(select(models.FinancingOffer).where(models.FinancingOffer.organization_id==user.organization_id).order_by(models.FinancingOffer.id.desc())).all()
    return [{"id":o.id,"customer_id":o.customer_id,"invoice_id":o.invoice_id,"requested_minor":o.requested_minor,"risk_score":o.risk_score,"status":o.status,"rationale":o.rationale,"created_at":o.created_at.isoformat()} for o in offers]

@app.get("/reports/receivables.csv")
def receivables_csv(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    from fastapi.responses import StreamingResponse
    invoices=db.scalars(select(models.Invoice).where(models.Invoice.organization_id==user.organization_id).order_by(models.Invoice.id)).all()
    out=io.StringIO(); writer=csv.writer(out); writer.writerow(["invoice_number","customer","amount_minor","paid_minor","outstanding_minor","currency","due_date","status"])
    for inv in invoices:
        c=db.get(models.Customer,inv.customer_id); writer.writerow([inv.invoice_number,c.name if c else "",inv.amount_minor,inv.paid_minor,inv.amount_minor-inv.paid_minor,inv.currency,inv.due_date,inv.status])
    return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=cashorbit-receivables.csv"})

class TeamUserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=12, max_length=128)
    role: str = "accountant"

@app.get("/team/users")
def list_team_users(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    members=db.scalars(select(models.User).where(models.User.organization_id==user.organization_id).order_by(models.User.id)).all()
    return [{"id":m.id,"email":m.email,"full_name":m.full_name,"role":m.role,"active":m.active} for m in members]

@app.post("/team/users")
def create_team_user(payload: TeamUserCreate, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    allowed={"owner","admin","accountant","collections","viewer"}
    if user.role not in {"owner","admin"}: raise HTTPException(status_code=403,detail="Only an owner or admin can add team members")
    role=payload.role.strip().lower()
    if role not in allowed: raise HTTPException(status_code=422,detail="Unsupported role")
    if user.role!="owner" and role in {"owner","admin"}: raise HTTPException(status_code=403,detail="Only the owner can assign owner/admin roles")
    email=payload.email.lower().strip()
    if db.scalar(select(models.User).where(models.User.email==email)): raise HTTPException(status_code=409,detail="Email is already registered")
    member=models.User(organization_id=user.organization_id,email=email,full_name=payload.full_name.strip(),password_hash=hash_password(payload.password),role=role)
    db.add(member); db.flush(); audit(db,user,"team.member_created","user",member.id,{"role":role,"email":email}); db.commit()
    return {"id":member.id,"email":member.email,"full_name":member.full_name,"role":member.role,"active":member.active}

@app.post("/portal/tokens/{token_id}/revoke")
def revoke_portal_token(token_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in {"owner","admin"}: raise HTTPException(status_code=403,detail="Only an owner or admin can revoke portal access")
    access=db.scalar(select(models.PortalToken).where(models.PortalToken.id==token_id,models.PortalToken.organization_id==user.organization_id))
    if not access: raise HTTPException(status_code=404,detail="Portal token not found")
    access.revoked=True; audit(db,user,"portal.token_revoked","portal_token",access.id,{"customer_id":access.customer_id}); db.commit()
    return {"token_id":access.id,"revoked":True}

class PlanChangeRequest(BaseModel):
    plan_code: str

@app.get("/billing/subscription")
def billing_subscription(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription=db.scalar(select(models.Subscription).where(models.Subscription.organization_id==user.organization_id))
    if not subscription:
        subscription=models.Subscription(organization_id=user.organization_id,plan_code="growth",status="demo_active",monthly_price_minor=0,simulated_period_end=(date.today()+timedelta(days=30)).isoformat())
        db.add(subscription); db.commit(); db.refresh(subscription)
    return {"id":subscription.id,"plan_code":subscription.plan_code,"status":subscription.status,"monthly_price_minor":subscription.monthly_price_minor,"period_end":subscription.simulated_period_end,"billing_mode":"demo_only_no_charges"}

@app.post("/billing/change-plan")
def change_demo_plan(payload: PlanChangeRequest, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role not in {"owner","admin"}: raise HTTPException(status_code=403,detail="Only an owner or admin can change the demo plan")
    plans={"starter":0,"growth":490000,"scale":1490000}
    code=payload.plan_code.strip().lower()
    if code not in plans: raise HTTPException(status_code=422,detail="Plan must be starter, growth, or scale")
    subscription=db.scalar(select(models.Subscription).where(models.Subscription.organization_id==user.organization_id))
    if not subscription:
        subscription=models.Subscription(organization_id=user.organization_id,plan_code=code,status="demo_active",monthly_price_minor=plans[code],simulated_period_end=(date.today()+timedelta(days=30)).isoformat()); db.add(subscription)
    else:
        subscription.plan_code=code; subscription.monthly_price_minor=plans[code]; subscription.status="demo_active"; subscription.simulated_period_end=(date.today()+timedelta(days=30)).isoformat()
    audit(db,user,"billing.demo_plan_changed","subscription",subscription.id,{"plan_code":code}); db.commit(); db.refresh(subscription)
    return {"plan_code":subscription.plan_code,"monthly_price_minor":subscription.monthly_price_minor,"status":subscription.status,"message":"Demo plan updated. No subscription charge was made."}

@app.get("/billing/usage")
def billing_usage(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    counts={"customers":db.scalar(select(func.count()).select_from(models.Customer).where(models.Customer.organization_id==user.organization_id)) or 0,"invoices":db.scalar(select(func.count()).select_from(models.Invoice).where(models.Invoice.organization_id==user.organization_id)) or 0,"team_members":db.scalar(select(func.count()).select_from(models.User).where(models.User.organization_id==user.organization_id)) or 0,"bank_transactions":db.scalar(select(func.count()).select_from(models.BankTransaction).where(models.BankTransaction.organization_id==user.organization_id)) or 0}
    limits={"starter":{"customers":25,"invoices":100,"team_members":2},"growth":{"customers":250,"invoices":2500,"team_members":10},"scale":{"customers":5000,"invoices":50000,"team_members":100}}
    subscription=db.scalar(select(models.Subscription).where(models.Subscription.organization_id==user.organization_id)); plan=subscription.plan_code if subscription else "growth"
    return {"plan_code":plan,"usage":counts,"illustrative_limits":limits.get(plan,limits["growth"]),"billing_mode":"demo_only_no_charges","note":"Usage limits are illustrative and not enforced as hard limits in this demo."}
