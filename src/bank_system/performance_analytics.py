"""ЛР9, варіант 4: відтворювана аналітика банківських операцій.

Дані синтетичні, суми зберігаються у цілих копійках, щоб уникати
помилок округлення фінансових операцій.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from random import Random
from collections import defaultdict
import numpy as np

@dataclass(frozen=True)
class BankDataset:
    balances: tuple[int, ...]
    account_ids: tuple[int, ...]
    amounts: tuple[int, ...]  # >0 deposit, <0 withdrawal


def generate_dataset(accounts: int = 100_000, transactions: int = 500_000, seed: int = 42) -> BankDataset:
    """Генерує валідні рахунки та журнал; транзакції — демонстраційні події.

    Поточний баланс не обчислюється як початковий плюс цей журнал: журнал
    демонструє оборот, а balances є незалежним поточним зрізом рахунків.
    """
    if accounts <= 0 or transactions <= 0:
        raise ValueError('Кількості мають бути додатними')
    rng = Random(seed)
    balances = tuple(rng.randrange(10_000, 2_000_000) for _ in range(accounts))
    ids = tuple(rng.randrange(accounts) for _ in range(transactions))
    amounts = tuple((1 if rng.randrange(2) else -1) * rng.randrange(100, 100_000)
                    for _ in range(transactions))
    return BankDataset(balances, ids, amounts)


def statistics_python(data: BankDataset) -> dict[str, int]:
    """Baseline: Python-цикли для суми балансу, обороту та статистики."""
    total = 0
    for balance in data.balances:
        total += balance
    incoming = outgoing = count_in = count_out = 0
    for amount in data.amounts:
        if amount >= 0:
            incoming += amount
            count_in += 1
        else:
            outgoing -= amount
            count_out += 1
    return {'total_balance': total, 'incoming': incoming, 'outgoing': outgoing,
            'turnover': incoming + outgoing, 'deposits': count_in, 'withdrawals': count_out}


def statistics_numpy(data: BankDataset) -> dict[str, int]:
    balances = np.asarray(data.balances, dtype=np.int64)
    amounts = np.asarray(data.amounts, dtype=np.int64)
    deposits = amounts >= 0
    incoming = int(amounts[deposits].sum())
    outgoing = int(-amounts[~deposits].sum())
    return {'total_balance': int(balances.sum()), 'incoming': incoming,
            'outgoing': outgoing, 'turnover': incoming + outgoing,
            'deposits': int(np.count_nonzero(deposits)),
            'withdrawals': int(np.count_nonzero(~deposits))}


def history_balance_python(initial_cents: int, movements: tuple[int, ...]) -> int:
    """Перерахунок історії з перевіркою заборони від'ємного балансу."""
    balance = initial_cents
    for movement in movements:
        if balance + movement < 0:
            raise ValueError('Недостатньо коштів')
        balance += movement
    return balance


def account_turnover_python(ids: tuple[int, ...], amounts: tuple[int, ...], account_id: int) -> int:
    return sum(abs(value) for idx, value in zip(ids, amounts) if idx == account_id)


class CachedAccountAnalytics:
    """Індексований підрахунок із очищенням кешу після зміни журналу."""
    def __init__(self, ids: tuple[int, ...], amounts: tuple[int, ...]):
        self.by_account: dict[int, list[int]] = defaultdict(list)
        for account_id, amount in zip(ids, amounts):
            self.by_account[account_id].append(amount)

    @lru_cache(maxsize=1024)
    def turnover(self, account_id: int) -> int:
        return sum(abs(amount) for amount in self.by_account.get(account_id, ()))

    def add_transaction(self, account_id: int, amount: int) -> None:
        self.by_account[account_id].append(amount)
        self.turnover.cache_clear()
