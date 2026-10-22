import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from bank_system.models import Base, Account, Client
from bank_system.value_objects import Money

@pytest.fixture
def sample_money() -> Money:
    return Money(amount=500.0, currency="UAH")

@pytest.fixture
def session() -> Session:
    """Ізольована тестова база даних у пам'яті для інтеграційних тестів."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, expire_on_commit=False)
    
    with TestSession() as session:
        yield session
    
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_client(session: Session) -> Client:
    client = Client(name="Максим Войтович")
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@pytest.fixture
def sample_account(session: Session, sample_client: Client) -> Account:
    account = Account(
        account_number="ACC-12345",
        balance=1500.0,
        account_type="Debit",
        client_id=sample_client.id
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@pytest.fixture
def account_factory(session: Session, sample_client: Client):
    def _create(acc_num: str = "ACC-001", balance: float = 1000.0, acc_type: str = "Standard") -> Account:
        account = Account(
            account_number=acc_num,
            balance=balance,
            account_type=acc_type,
            client_id=sample_client.id
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return account
    return _create