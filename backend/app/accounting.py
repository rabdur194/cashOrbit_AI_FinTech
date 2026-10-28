from fastapi import HTTPException
from sqlalchemy.orm import Session
from .models import JournalEntry, JournalLine, AuditEvent, User
import json

def post_journal(db: Session, user: User, reference_type: str, reference_id: int, memo: str, lines: list[dict]) -> JournalEntry:
    debit = sum(x.get("debit_minor", 0) for x in lines)
    credit = sum(x.get("credit_minor", 0) for x in lines)
    if debit <= 0 or debit != credit:
        raise HTTPException(status_code=400, detail="Journal entry must have equal, positive total debits and credits")
    entry = JournalEntry(organization_id=user.organization_id, reference_type=reference_type, reference_id=reference_id, memo=memo)
    entry.lines = [JournalLine(account_code=x["account_code"], account_name=x["account_name"], debit_minor=x.get("debit_minor",0), credit_minor=x.get("credit_minor",0)) for x in lines]
    db.add(entry)
    db.flush()
    db.add(AuditEvent(organization_id=user.organization_id, actor_user_id=user.id, action="ledger.entry_posted", entity_type="journal_entry", entity_id=entry.id, details=json.dumps({"reference_type": reference_type, "reference_id": reference_id})))
    return entry

def audit(db: Session, user: User, action: str, entity_type: str, entity_id: int | None, details: dict | None = None):
    db.add(AuditEvent(organization_id=user.organization_id, actor_user_id=user.id, action=action, entity_type=entity_type, entity_id=entity_id, details=json.dumps(details or {})))
