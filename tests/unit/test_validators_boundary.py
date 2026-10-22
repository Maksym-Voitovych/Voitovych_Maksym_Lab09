import pytest
from bank_system.models import BankAccount
from bank_system.value_objects import Money

@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(-0.01, id="just_below_zero"),
        pytest.param(-100.0, id="negative_large"),
    ],
)
def test_invalid_amounts_raise_error(amount: float) -> None:
    with pytest.raises(ValueError):
        Money(amount=amount, currency="UAH")


@pytest.mark.parametrize(
    "amount",
    [
        pytest.param(0.0, id="zero_boundary"),
        pytest.param(0.01, id="just_above_zero"),
        pytest.param(99999.99, id="large_amount"),
    ],
)
def test_valid_amounts_accepted(amount: float) -> None:
    m = Money(amount=amount, currency="UAH")
    assert m.amount == pytest.approx(amount)