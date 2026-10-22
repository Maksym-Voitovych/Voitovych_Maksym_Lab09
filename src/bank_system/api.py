from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from bank_system.database import SessionLocal
from bank_system.models import Client, Account, Transaction
from bank_system.repositories import ClientRepository, AccountRepository
from bank_system.schemas import (
    ClientCreate, ClientResponse,
    AccountCreate, AccountResponse,
    AmountOperation, TransferRequest,
    TransactionResponse
)
from bank_system.external_api import fetch_many_accounts_parallel
import asyncio

app = FastAPI(title="Bank System API", version="1.0.0")

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientCreate, session: Session = Depends(get_session)) -> ClientResponse:
    repo = ClientRepository(session)
    try:
        client = repo.add(full_name=data.full_name, email=data.email)
    except TypeError:
        try:
            client = repo.add(name=data.full_name)
        except TypeError:
            client = repo.add(data.full_name)
            
    return ClientResponse(
        id=client.id,
        full_name=client.full_name if hasattr(client, 'full_name') else data.full_name,
        email=client.email if hasattr(client, 'email') else data.email
    )

@app.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, session: Session = Depends(get_session)) -> ClientResponse:
    repo = ClientRepository(session)
    client = repo.get_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientResponse(
        id=client.id,
        full_name=client.full_name,
        email=client.email
    )

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(data: AccountCreate, session: Session = Depends(get_session)) -> Account:
    repo = AccountRepository(session)
    account_number = f"ACC-{data.client_id}-{int(asyncio.get_event_loop().time())}"
    try:
        return repo.add(
            account_number=account_number,
            balance=data.initial_balance,
            client_id=data.client_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, session: Session = Depends(get_session)) -> Account:
    repo = AccountRepository(session)
    account = repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.get("/accounts", response_model=list[AccountResponse])
async def get_accounts(session: Session = Depends(get_session)) -> list[Account]:
    repo = AccountRepository(session)
    return repo.get_all()

@app.post("/accounts/{account_id}/deposit", response_model=AccountResponse)
async def deposit(account_id: int, data: AmountOperation, session: Session = Depends(get_session)) -> Account:
    repo = AccountRepository(session)
    account = repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    new_balance = account.balance + data.amount
    updated_account = repo.update_balance(account_id, new_balance)
    return updated_account

@app.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
async def withdraw(account_id: int, data: AmountOperation, session: Session = Depends(get_session)) -> Account:
    repo = AccountRepository(session)
    account = repo.get_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.balance < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    new_balance = account.balance - data.amount
    updated_account = repo.update_balance(account_id, new_balance)
    return updated_account

@app.post("/accounts/batch-fetch")
async def batch_fetch_accounts(account_ids: list[int]) -> list[dict]:
    try:
        return await asyncio.wait_for(
            fetch_many_accounts_parallel("http://127.0.0.1:8000", account_ids),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Batch operation timed out")