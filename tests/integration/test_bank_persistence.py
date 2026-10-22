import pytest
from bank_system.models import Client, Account
from bank_system.repositories import ClientRepository, AccountRepository
from bank_system.services import BankService

def test_crud_client_and_account(session) -> None:
    client_repo = ClientRepository(session)
    account_repo = AccountRepository(session)

    # Створення клієнта (Create)
    client = client_repo.add("Максим Войтович")
    assert client.id is not None
    assert client.name == "Максим Войтович"

    # Створення рахунку (Create)
    account = account_repo.add("UA123456789", 1500.0, client.id, "Debit")
    assert account.balance == 1500.0

    # Читання (Read)
    loaded = account_repo.get_by_number("UA123456789")
    assert loaded is not None
    assert loaded.account_type == "Debit"

    # Оновлення (Update)
    account_repo.update_balance(account.id, 2000.0)
    assert account_repo.get_by_id(account.id).balance == 2000.0

    # Видалення (Delete)
    assert account_repo.delete(account.id) is True
    assert account_repo.get_by_id(account.id) is None

def test_negative_balance_forbidden(session) -> None:
    client_repo = ClientRepository(session)
    account_repo = AccountRepository(session)
    client = client_repo.add("Тест Тестов")

    # Перевірка заборони від'ємного балансу
    with pytest.raises(ValueError):
        account_repo.add("UA00000000", -100.0, client.id)

def test_transfer_money_success(session) -> None:
    client_repo = ClientRepository(session)
    account_repo = AccountRepository(session)
    service = BankService(session)

    client = client_repo.add("Олена")
    acc1 = account_repo.add("UA111", 2000.0, client.id)
    acc2 = account_repo.add("UA222", 500.0, client.id)

    # Успішний переказ коштів
    service.transfer_money("UA111", "UA222", 300.0)

    assert account_repo.get_by_number("UA111").balance == 1700.0
    assert account_repo.get_by_number("UA222").balance == 800.0

def test_transfer_money_rollback_on_insufficient_funds(session) -> None:
    client_repo = ClientRepository(session)
    account_repo = AccountRepository(session)
    service = BankService(session)

    client = client_repo.add("Петро")
    acc1 = account_repo.add("UA333", 100.0, client.id)
    acc2 = account_repo.add("UA444", 500.0, client.id)

    # Спроба переказати більше, ніж є на рахунку -> викличе помилку та rollback
    with pytest.raises(ValueError):
        service.transfer_money("UA333", "UA444", 1000.0)

    # Перевірка, що завдяки rollback баланси залишилися незмінними
    assert account_repo.get_by_number("UA333").balance == 100.0
    assert account_repo.get_by_number("UA444").balance == 500.0