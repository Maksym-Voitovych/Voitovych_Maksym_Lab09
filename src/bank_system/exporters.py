from collections.abc import Iterable
import json
from pathlib import Path

from bank_system.exceptions import DataExportError
from bank_system.models import BankAccount

def export_accounts_json(accounts: Iterable[BankAccount], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    count = 0
    try:
        with temporary.open("w", encoding="utf-8") as file:
            file.write("[\n")
            first = True
            for account in accounts:
                if not first:
                    file.write(",\n")
                json.dump(account.to_dict(), file, ensure_ascii=False, indent=2)
                first = False
                count += 1
            file.write("\n]\n")
        temporary.replace(path)
    except (OSError, TypeError) as error:
        temporary.unlink(missing_ok=True)
        raise DataExportError(f"Cannot export data to {path}") from error
    return count