import pytest
from bank_system.value_objects import Money

def test_money_creation(sample_money):
    assert sample_money.amount == 500.0
    assert sample_money.currency == "UAH"
    assert str(sample_money) == "500.00 UAH"

def test_negative_money_raises_error():
    with pytest.raises(ValueError, match="Сума грошей не може бути від'ємною"):
        Money(amount=-50.0)

@pytest.mark.parametrize(
    "amount, expected_amount",
    [
        (0.0, 0.0),
        (999.99, 999.99),
        (0.1 + 0.2, 0.3),
    ],
)
def test_valid_money_amounts(amount, expected_amount):
    m = Money(amount=amount)
    assert m.amount == pytest.approx(expected_amount)

def test_money_addition():
    m1 = Money(100.0, "UAH")
    m2 = Money(50.0, "UAH")
    result = m1 + m2
    assert result.amount == 150.0

def test_money_subtraction():
    m1 = Money(100.0, "UAH")
    m2 = Money(40.0, "UAH")
    result = m1 - m2
    assert result.amount == 60.0

def test_money_currency_mismatch_addition():
    m1 = Money(100.0, "UAH")
    m2 = Money(100.0, "USD")
    with pytest.raises(ValueError, match="різних валютах"):
        _ = m1 + m2

def test_money_subtraction_negative_result():
    m1 = Money(50.0, "UAH")
    m2 = Money(100.0, "UAH")
    with pytest.raises(ValueError, match="не може бути від'ємним"):
        _ = m1 - m2

def test_money_comparison():
    m1 = Money(50.0, "UAH")
    m2 = Money(100.0, "UAH")
    assert m1 < m2
    assert m2 > m1
    
    with pytest.raises(ValueError, match="різних валютах"):
        _ = m1 < Money(10.0, "USD")