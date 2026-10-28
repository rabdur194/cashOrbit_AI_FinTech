from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class LoginRequest(BaseModel):
    email: str
    password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: str = ""
class CustomerOut(BaseModel):
    id: int; name: str; email: str
    model_config = ConfigDict(from_attributes=True)
class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_number: str = Field(min_length=2, max_length=50)
    description: str = "Services"
    amount_minor: int = Field(gt=0)
    currency: str = "BDT"
    due_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
class PaymentCreate(BaseModel):
    amount_minor: int = Field(gt=0)
    reference: str = ""
    method: str = "manual"
class ReconcileRequest(BaseModel):
    transaction_id: int
    payment_id: int
