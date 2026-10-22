from .decorators import log_execution

@log_execution(prefix="[PROCESSOR]")
def build_account_index(accounts: list) -> dict:
    return {acc["account_number"]: acc for acc in accounts}

def find_account(index: dict, account_number: str) -> dict:
    return index.get(account_number)

def create_min_balance_filter(min_balance: float):
    """Closure для створення фільтра."""
    def predicate(account: dict) -> bool:
        return account["balance"] >= min_balance
    return predicate

@log_execution(prefix="[PROCESSOR]")
def filter_accounts(accounts: list, predicate_func) -> list:
    return [acc for acc in accounts if predicate_func(acc)]

@log_execution(prefix="[PROCESSOR]")
def universal_sort(accounts: list, key: str = "balance", reverse: bool = False) -> list:
    """
    Універсальне сортування за будь-яким полем словника.
    """
    return sorted(accounts, key=lambda acc: acc.get(key, 0), reverse=reverse)