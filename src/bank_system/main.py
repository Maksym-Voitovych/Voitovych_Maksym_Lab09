import logging
from pathlib import Path

from bank_system.config import load_config
from bank_system.exceptions import ApplicationError
from bank_system.exporters import export_accounts_json
from bank_system.logging_config import configure_logging
from bank_system.services import ImportStatistics, import_accounts
from bank_system.utils import logged_operation

logger = logging.getLogger(__name__)

def main() -> None:
    try:
        config = load_config(Path("config.yaml"))
        configure_logging(config.logging.level, config.logging.path)

        statistics = ImportStatistics()
        with logged_operation("Bank account import/export"):
            accounts = import_accounts(
                config.input_path,
                skip_invalid=config.processing.skip_invalid,
                statistics=statistics,
            )
            exported = export_accounts_json(accounts, config.output_path)

        logger.info(
            "Total=%s, valid=%s, invalid=%s, exported=%s",
            statistics.total,
            statistics.valid,
            statistics.invalid,
            exported,
        )
    except ApplicationError as error:
        logger.error("Application error: %s", error)
        raise SystemExit(1) from error

if __name__ == "__main__":
    main()