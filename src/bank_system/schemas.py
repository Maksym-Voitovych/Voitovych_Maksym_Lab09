from pydantic import BaseModel, Field
from datetime import datetime

class ClientCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: str

class ClientResponse(BaseModel):
    id: int
    full_name: str
    email: str
    model_config = {"from_attributes": True}

class AccountCreate(BaseModel):
    client_id: int = Field(gt=0)
    initial_balance: float = Field(ge=0)

class AccountResponse(BaseModel):
    id: int
    client_id: int
    balance: float
    model_config = {"from_attributes": True}

class AmountOperation(BaseModel):
    amount: float = Field(gt=0)

class TransferRequest(BaseModel):
    sender_account_id: int = Field(gt=0)
    receiver_account_id: int = Field(gt=0)
    amount: float = Field(gt=0)

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    operation_type: str
    amount: float
    timestamp: datetime
    model_config = {"from_attributes": True}