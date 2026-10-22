import sqlite3
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from bank_system.models import Account, Transaction

class BankService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_total_funds(self) -> float:
        statement = select(func.sum(Account.balance))
        result = self.session.scalar(statement)
        return float(result) if result else 0.0

    def transfer_money(self, sender_number: str, receiver_number: str, amount: float) -> None:
        """Транзакційна операція з атомарністю (commit / rollback)."""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        
        try:
            sender = self.session.scalar(select(Account).where(Account.account_number == sender_number))
            receiver = self.session.scalar(select(Account).where(Account.account_number == receiver_number))

            if not sender or not receiver:
                raise ValueError("Sender or receiver account not found.")
            if sender.balance < amount:
                raise ValueError("Insufficient funds for transfer.")

            sender.balance -= amount
            receiver.balance += amount

            tx = Transaction(
                sender_account_id=sender.id,
                receiver_account_id=receiver.id,
                amount=amount,
            )
            self.session.add(tx)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise


def find_account_by_number_db_api(database_path: str, account_number: str) -> tuple | None:
    """Приклад використання стандартного DB-API із параметризацією."""
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT accounts.account_number, accounts.balance, clients.name
            FROM accounts
            JOIN clients ON accounts.client_id = clients.id
            WHERE accounts.account_number = ?
            """,
            (account_number,),
        )
        return cursor.fetchone()