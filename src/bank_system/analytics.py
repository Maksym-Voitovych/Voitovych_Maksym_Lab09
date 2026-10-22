from collections import defaultdict, Counter, deque
from .decorators import log_execution

operation_history = deque(maxlen=5)

def add_to_history(action: str) -> None:
    """Додає дію до історії (deque)."""
    operation_history.append(action)

def get_history() -> list:
    """Повертає список останніх операцій."""
    return list(operation_history)

@log_execution(prefix="[ANALYTICS]")
def get_account_type_stats(accounts: list) -> Counter:
    """
    Формує статистику кількості рахунків за типами.
    Використовує Counter з модуля collections.
    """
    return Counter(acc["account_type"] for acc in accounts)

@log_execution(prefix="[ANALYTICS]")
def group_accounts_by_type(accounts: list) -> dict:
    grouped = defaultdict(list)
    for acc in accounts:
        grouped[acc["account_type"]].append(acc)
    return dict(grouped)

def calculate_total_balance(*balances: float) -> float:
    return sum(balances)

def get_average_balance(accounts: list) -> float:
    if not accounts:
        return 0.0
    return sum(acc["balance"] for acc in accounts) / len(accounts)

def get_max_balance_account(accounts: list) -> dict:
    if not accounts:
        return {}
    return max(accounts, key=lambda acc: acc["balance"])