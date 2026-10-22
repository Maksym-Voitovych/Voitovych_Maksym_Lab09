from unittest.mock import AsyncMock
import pytest
from bank_system.exceptions import ConfigurationError

@pytest.mark.asyncio
async def test_async_banking_operation_success() -> None:
    client = AsyncMock()
    client.fetch_account_status.return_value = {"status": "active", "balance": 1500.0}
    
    # Симуляція виклику асинхронного сервісу/клієнта
    status = await client.fetch_account_status("ACC-12345")
    assert status["status"] == "active"
    client.fetch_account_status.assert_awaited_once_with("ACC-12345")


@pytest.mark.asyncio
async def test_async_banking_operation_failure() -> None:
    client = AsyncMock()
    client.fetch_account_status.side_effect = ConnectionError("Bank API unavailable")
    
    with pytest.raises(ConnectionError, match="Bank API unavailable"):
        await client.fetch_account_status("ACC-12345")