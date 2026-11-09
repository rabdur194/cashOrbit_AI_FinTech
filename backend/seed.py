"""
CashOrbit demo seed
-------------------
Creates:
  - Organization: CashOrbit Demo
  - User: demo@cashorbit.local / CashOrbitDemo123!
  - 3 customers + 6 invoices (some overdue, some paid)

Where to put it:
  backend/seed.py  (next to app/ folder)

How to run locally:
  cd backend
  python seed.py

How to run on Render (after deploy):
  Render Dashboard -> your API service -> Shell tab
  python seed.py

It is idempotent - you can run it twice, it won't create duplicates.
If demo user already exists, it will reset its password to CashOrbitDemo123!
"""

import os
import sys
from datetime import date, timedelta

# Make sure `app` package is importable when running `python seed.py` from backend/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.database import SessionLocal, engine
from app import models


# --- password hashing: use the SAME function your auth uses ---
# Try the common places first, fall back to bcrypt directly.
def hash_password(plain: str) -> str:
    try:
        from app.security import get_password_hash  # most likely in your project
        return get_password_hash(plain)
    except Exception:
        pass
    try:
        from app.auth import get_password_hash
        return get_password_hash(plain)
    except Exception:
        pass
    try:
        from passlib.context import CryptContext
        return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(plain)
    except Exception:
        pass
    # Last resort: bcrypt directly
    import bcrypt
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def get_or_create_organization(db, name="CashOrbit Demo"):
    # Try common model names: Organization / Organisation / Workspace
    Org = getattr(models, "Organization", None) or getattr(models, "Organisation", None) or getattr(models, "Workspace", None)
    if Org is None:
        raise RuntimeError("No Organization model found in app.models. Check your models.py")
    org = db.scalars(select(Org).where(Org.name == name)).first()
    if org:
        return org
    org = Org(name=name)
    db.add(org)
    db.commit()
    db.refresh(org)
    print(f"Created organization: {org.name} (id={org.id})")
    return org


def get_or_create_user(db, org, email="demo@cashorbit.local", password="CashOrbitDemo123!"):
    User = getattr(models, "User", None)
    if User is None:
        raise RuntimeError("No User model found in app.models")
    user = db.scalars(select(User).where(User.email == email)).first()
    hashed = hash_password(password)
    if user:
        # reset password + link to org so login always works
        user.hashed_password = hashed
        # some projects use password_hash, some use hashed_password
        if hasattr(user, "password_hash"):
            user.password_hash = hashed
        if hasattr(user, "organization_id"):
            user.organization_id = org.id
        if hasattr(user, "is_active"):
            user.is_active = True
        db.commit()
        print(f"Reset demo user password: {email}")
        return user

    # Build kwargs dynamically - different projects name fields differently
    kwargs = {"email": email}
    if hasattr(User, "hashed_password"):
        kwargs["hashed_password"] = hashed
    if hasattr(User, "password_hash"):
        kwargs["password_hash"] = hashed
    if hasattr(User, "full_name"):
        kwargs["full_name"] = "Demo User"
    if hasattr(User, "name"):
        kwargs["name"] = "Demo User"
    if hasattr(User, "organization_id"):
        kwargs["organization_id"] = org.id
    if hasattr(User, "is_active"):
        kwargs["is_active"] = True
    if hasattr(User, "is_superuser"):
        kwargs["is_superuser"] = False

    user = User(**kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created demo user: {email} / {password} (id={user.id})")
    return user


def seed_customers_and_invoices(db, org):
    Customer = getattr(models, "Customer", None)
    Invoice = getattr(models, "Invoice", None)
    if Customer is None or Invoice is None:
        print("Skipping customers/invoices - Customer/Invoice model not found")
        return

    # Only seed if no invoices yet for this org
    existing = db.scalars(select(Invoice).where(Invoice.organization_id == org.id).limit(1)).first()
    if existing:
        print("Invoices already exist - skipping invoice seed")
        return

    today = date.today()
    customers_data = [
        ("Acme Trading Ltd", "acme@example.com"),
        ("Bright Retail Co", "bright@example.com"),
        ("Northwind Supplies", "northwind@example.com"),
    ]
    customers = []
    for name, email in customers_data:
        c_kwargs = {"name": name, "organization_id": org.id}
        if hasattr(Customer, "email"):
            c_kwargs["email"] = email
        c = Customer(**c_kwargs)
        db.add(c)
        customers.append(c)
    db.commit()
    for c in customers:
        db.refresh(c)

    # amount_minor = amount * 100, e.g. 125000 = 1250.00
    invoices_data = [
        # (customer_idx, invoice_number, description, amount_minor, paid_minor, due_offset_days, status)
        (0, "INV-1001", "Wholesale order - March", 125000, 0, -12, "sent"),
        (0, "INV-1002", "Wholesale order - April", 84000, 84000, -5, "paid"),
        (1, "INV-1003", "Retail supply", 45200, 0, -3, "sent"),
        (1, "INV-1004", "Retail supply - urgent", 98000, 20000, 7, "sent"),
        (2, "INV-1005", "Office supplies", 31000, 0, 14, "sent"),
        (2, "INV-1006", "Bulk order", 210000, 0, -20, "sent"),
    ]
    for idx, number, desc, amount, paid, due_offset, status in invoices_data:
        inv_kwargs = {
            "organization_id": org.id,
            "customer_id": customers[idx].id,
            "invoice_number": number,
            "description": desc,
            "currency": "BDT",
            "amount_minor": amount,
            "paid_minor": paid,
            "due_date": today + timedelta(days=due_offset),
            "status": status,
        }
        # Only keep fields that actually exist on your Invoice model
        inv_kwargs = {k: v for k, v in inv_kwargs.items() if hasattr(Invoice, k)}
        inv = Invoice(**inv_kwargs)
        db.add(inv)
    db.commit()
    print(f"Created {len(invoices_data)} demo invoices (2 overdue, 1 paid, 3 upcoming)")


def main():
    # Create tables if they don't exist (safe - won't drop data)
    try:
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"create_all warning (tables may already exist): {e}")

    db = SessionLocal()
    try:
        org = get_or_create_organization(db)
        get_or_create_user(db, org)
        seed_customers_and_invoices(db, org)
        print("\nSEED DONE")
        print("Login with:")
        print("  Email: demo@cashorbit.local")
        print("  Password: CashOrbitDemo123!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
