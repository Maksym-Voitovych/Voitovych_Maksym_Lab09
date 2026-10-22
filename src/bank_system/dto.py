from typing import TypedDict


class AccountPayload(TypedDict):
    account_number: str
    customer_id: int
    customer_name: str
    customer_email: str
    initial_amount: float
    currency: str
    account_type: str