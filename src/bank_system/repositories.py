from sqlalchemy import select
from sqlalchemy.orm import Session
from bank_system.models import Client, Account, Transaction

class ClientRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, name: str) -> Client:
        client = Client(name=name)
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_by_id(self, client_id: int) -> Client | None:
        return self.session.get(Client, client_id)


class AccountRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, account_number: str, balance: float, client_id: int, account_type: str = "Standard") -> Account:
        if balance < 0:
            raise ValueError("Balance cannot be negative.")
        account = Account(
            account_number=account_number,
            balance=balance,
            client_id=client_id,
            account_type=account_type,
        )
        self.session.add(account)
        self.session.commit()
        self.session.refresh(account)
        return account

    def get_by_id(self, account_id: int) -> Account | None:
        return self.session.get(Account, account_id)

    def get_by_number(self, account_number: str) -> Account | None:
        statement = select(Account).where(Account.account_number == account_number)
        return self.session.scalar(statement)

    def get_all(self) -> list[Account]:
        statement = select(Account)
        return list(self.session.scalars(statement))

    def update_balance(self, account_id: int, new_balance: float) -> Account | None:
        if new_balance < 0:
            raise ValueError("Balance cannot be negative.")
        account = self.get_by_id(account_id)
        if account is None:
            return None
        account.balance = new_balance
        self.session.commit()
        self.session.refresh(account)
        return account

    def delete(self, account_id: int) -> bool:
        account = self.get_by_id(account_id)
        if account is None:
            return False
        self.session.delete(account)
        self.session.commit()
        return True