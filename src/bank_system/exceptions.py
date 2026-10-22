class ApplicationError(Exception):
    """Base application exception."""

class ConfigurationError(ApplicationError):
    """Configuration is invalid or missing."""

class DataError(ApplicationError):
    """Base data exception."""

class DataImportError(DataError):
    """Input data cannot be imported."""

class RecordValidationError(DataError):
    """Record fails validation rules."""
    def __init__(
        self,
        message: str,
        *,
        line_number: int | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.field = field

class DataExportError(DataError):
    """Output cannot be written."""