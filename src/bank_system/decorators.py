from functools import wraps
import time

def log_execution(prefix="[LOG]"):
    """Параметризований декоратор для логування з можливістю вибору префікса."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            print(f"{prefix} Виклик функції: {func.__name__}")
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{prefix} {func.__name__} виконано за {end_time - start_time:.6f} сек.")
            return result
        return wrapper
    return decorator