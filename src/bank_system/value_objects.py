from dataclasses import dataclass
from datetime import datetime
from functools import total_ordering


@total_ordering
@dataclass(frozen=True, slots=True)
class Money:
    amount: float
    currency: str = "UAH"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Сума грошей не може бути від'ємною")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Неможливо додати гроші в різних валютах")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Неможливо відняти гроші в різних валютах")
        if self.amount - other.amount < 0:
            raise ValueError("Результат не може бути від'ємним")
        return Money(self.amount - other.amount, self.currency)

    def __lt__(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Неможливо порівняти гроші в різних валютах")
        return self.amount < other.amount

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


@dataclass(frozen=True, slots=True)
class Transaction:
    id: int
    account_number: str
    amount: Money
    transaction_type: str  # "deposit" або "withdraw"
    timestamp: datetime = datetime.now()