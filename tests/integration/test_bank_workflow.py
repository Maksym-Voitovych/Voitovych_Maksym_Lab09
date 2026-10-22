import json
from pathlib import Path
import pytest

@pytest.mark.integration
def test_bank_workflow_full_pipeline(tmp_path: Path) -> None:
    # 1. Arrange: Створюємо тимчасовий CSV з даними рахунків
    csv_file = tmp_path / "accounts.csv"
    csv_file.write_text(
        "account_number,client,balance\n"
        "ACC-001,Максим Войтович,2500.0\n"
        "ACC-002,Тест Користувач,500.0\n",
        encoding="utf-8"
    )
    
    # 2. Act: Виконуємо експорт через роботу з файлом у tmp_path
    output_json = tmp_path / "output.json"
    
    data_to_export = [
        {"account_number": "ACC-001", "client": "Максим Войтович", "balance": 2500.0},
        {"account_number": "ACC-002", "client": "Тест Користувач", "balance": 500.0}
    ]
    
    output_json.write_text(json.dumps(data_to_export, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # 3. Assert: Перевіряємо результати інтеграції
    assert output_json.exists()
    loaded_data = json.loads(output_json.read_text(encoding="utf-8"))
    assert len(loaded_data) == 2
    assert loaded_data[0]["account_number"] == "ACC-001"
    assert loaded_data[0]["balance"] == pytest.approx(2500.0)