import json
from bank_system.exporters import export_accounts_json
from bank_system.models import BankAccount
from bank_system.exceptions import DataExportError
import pytest

def test_export_accounts_success(tmp_path, sample_account):
    file_path = tmp_path / "output" / "accounts.json"
    accounts = [sample_account]
    
    count = export_accounts_json(accounts, file_path)
    
    assert count == 1
    assert file_path.exists()
    
    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["account_number"] == "ACC-12345"
    assert data[0]["client"] == "Максим Войтович"

def test_export_accounts_failure_raises_error(tmp_path):
    with pytest.raises(DataExportError):
        export_accounts_json([], path=tmp_path)