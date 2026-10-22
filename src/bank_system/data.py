ACCOUNT_TYPES = ("Checking", "Savings", "Credit", "Deposit")
def create_account(**kwargs) -> dict:
    """
    Створює словник із даними рахунку.
    Використовує **kwargs для гнучкої передачі параметрів.
    """
    required_keys = {"client_name", "account_number", "balance", "account_type"}
    
    if not required_keys.issubset(kwargs.keys()):
        raise ValueError(f"Missing required fields: {required_keys - kwargs.keys()}")
        
    return dict(kwargs)

def get_sample_accounts() -> list:
    """Повертає початковий список рахунків (list of dicts)."""
    return [
        create_account(client_name="Олександр", account_number="UA1001", balance=15000.50, account_type="Checking"),
        create_account(client_name="Марія", account_number="UA1002", balance=42000.00, account_type="Savings"),
        create_account(client_name="Іван", account_number="UA1003", balance=-500.00, account_type="Credit"),
        create_account(client_name="Олександр", account_number="UA1004", balance=120000.00, account_type="Deposit"),
        create_account(client_name="Анна", account_number="UA1005", balance=8500.75, account_type="Checking"),
    ]