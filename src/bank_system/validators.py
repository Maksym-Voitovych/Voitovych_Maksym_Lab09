from bank_system.exceptions import RecordValidationError
from bank_system.models import BankAccount

def parse_bank_account(row: dict[str, str], *, line_number: int) -> BankAccount:
    try:
        account_number = str(row["account_number"]).strip()
        if not account_number:
            raise ValueError("Account number is empty")
    except (KeyError, ValueError) as error:
        raise RecordValidationError("Invalid account number", line_number=line_number, field="account_number") from error

    client = str(row.get("client", "")).strip()
    if not client:
        raise RecordValidationError("Client name is empty", line_number=line_number, field="client")

    try:
        balance = float(row["balance"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError("Invalid balance value", line_number=line_number, field="balance") from error

    if balance < 0:
        raise RecordValidationError("Balance cannot be negative", line_number=line_number, field="balance")

    operation = str(row.get("operation", "")).strip().lower()
    if operation not in ("deposit", "withdraw"):
        raise RecordValidationError("Invalid operation (must be deposit or withdraw)", line_number=line_number, field="operation")

    try:
        amount = float(row["amount"])
    except (KeyError, TypeError, ValueError) as error:
        raise RecordValidationError("Invalid amount value", line_number=line_number, field="amount") from error

    if amount <= 0:
        raise RecordValidationError("Amount must be greater than zero", line_number=line_number, field="amount")

    # Контроль недопущення від’ємного балансу після операції списання
    final_balance = balance
    if operation == "deposit":
        final_balance += amount
    elif operation == "withdraw":
        if balance - amount < 0:
            raise RecordValidationError("Insufficient funds: operation results in negative balance", line_number=line_number, field="amount")
        final_balance -= amount

    return BankAccount(
        account_number=account_number,
        client=client,
        balance=round(final_balance, 2),
        operation=operation,
        amount=amount,
    )