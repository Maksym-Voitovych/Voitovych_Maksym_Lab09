import pytest
from pathlib import Path
from bank_system.services import import_accounts, ImportStatistics
from bank_system.exporters import export_accounts_json
from bank_system.exceptions import RecordValidationError

@pytest.mark.integration
def test_csv_import_and_json_export_pipeline(tmp_path):
    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(
        "account_number,client,balance,operation,amount\n"
        "ACC-001,Максим Войтович,1000.0,deposit,500.0\n"
        "ACC-002,Олег Іванов,2000.0,withdraw,200.0\n",
        encoding="utf-8"
    ) 
    stats = ImportStatistics()
    accounts = list(import_accounts(csv_file, skip_invalid=False, statistics=stats))
    
    assert stats.total == 2
    assert stats.valid == 2
    assert stats.invalid == 0
    assert len(accounts) == 2
    assert accounts[0].account_number == "ACC-001"
    assert accounts[1].client == "Олег Іванов"
    output_json = tmp_path / "output" / "exported_accounts.json"
    count = export_accounts_json(accounts, output_json)
    
    assert count == 2
    assert output_json.exists()
@pytest.mark.integration
def test_csv_import_malformed_record_raises_error(tmp_path):
    csv_file = tmp_path / "bad_accounts.csv"
    csv_file.write_text(
        "account_number,client,balance,operation,amount\n"
        "ACC-999,Невалідний,invalid_balance,deposit,100\n",
        encoding="utf-8"
    )
    
    stats = ImportStatistics()
    with pytest.raises((RecordValidationError, ValueError, TypeError)):
        list(import_accounts(csv_file, skip_invalid=False, statistics=stats))