# Лабораторна робота №8: Розробка REST API за допомогою FastAPI

**Тема:** Розробка асинхронного REST API для системи банківських рахунків із використанням FastAPI, SQLAlchemy ORM, Pydantic валідації, асинхронних запитів та інтеграційного тестування (Варіант 4).

**Автор:** Войтович Максим Андрійович (група ФеП-31).

## Опис проєкту

Проєкт доповнено сучасним веб-інтерфейсом та шаром API на базі **FastAPI**. Реалізовано повноцінні CRUD-операції для клієнтів та банківських рахунків, операції депозиту/зняття коштів, а також асинхронні batch-запити із застосуванням таймаутів та паралельної обробки через **HTTPX**. Для забезпечення надійності підключено валідацію вхідних і вихідних даних за допомогою **Pydantic**, а також налаштовано комплексне тестування через `pytest` і `TestClient`.

## Основні можливості та архітектура

- **FastAPI Application:** Побудовано швидкий асинхронний REST API із автоматичною генерацією документації (Swagger UI).
- **Pydantic Schemas:** Строга валідація даних для створення клієнтів (`ClientCreate`), рахунків (`AccountCreate`), операцій з коштами (`AmountOperation`) та серіалізація відповідей.
- **Dependency Injection:** Використання механізму залежностей FastAPI для керування сесіями бази даних (`get_session`).
- **Шар персистентності (SQLAlchemy ORM):** Використання реляційних моделей (`Client`, `Account`, `Transaction`) та паттерну Repository.
- **Асинхронність та зовнішні запити:** Реалізація паралельних запитів (`asyncio.gather`, `wait_for`) для пакетної обробки даних через HTTPX.
- **Тестування API:** Покриття функціоналу інтеграційними та API-тестами за допомогою `pytest`, `pytest-asyncio` та `TestClient`.

## Структура проєкту

```text
bank_system/
├── pyproject.toml
├── alembic.ini
├── README.md
├── bank_system.db
├── migrations/
│   └── versions/
├── src/
│   └── bank_system/
│       ├── __init__.py
│       ├── api.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── repositories.py
│       ├── services.py
│       └── external_api.py
└── tests/
    ├── conftest.py
    ├── test_api.py
    └── integration/
        └── test_bank_persistence.py
---

# Лабораторна робота №9 — Паралельність, багатопроцесність та оптимізація

**Варіант 4: Система банківських рахунків.** Продовження попереднього проєкту, базові REST API, ORM, сервіси та міграції збережені.

## Що реалізовано

- `src/bank_system/performance_analytics.py` — відтворювана генерація 100 000 рахунків та 500 000 операцій, baseline на Python, NumPy, історія балансу, індексований кеш із invalidation.
- `src/bank_system/parallel.py` — `threading.Thread`, `multiprocessing.Process`, `ThreadPoolExecutor`, `ProcessPoolExecutor`, синхронізація `Lock`, демонстрація race condition, потокове читання CSV.
- `benchmarks/benchmark_lab9.py` — п'ять повторів `perf_counter`, `timeit`, `cProfile`, `tracemalloc`, порівняння 1/2/4/8 workers, перевірки коректності, CSV, PNG графіки.
- `tests/unit/test_performance_lab9.py` — тести всіх реалізацій.

## Запуск (Windows PowerShell, з кореня проєкту)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python benchmarks/benchmark_lab9.py
python -m pytest -q
```

Швидка перевірка: `python benchmarks/benchmark_lab9.py --quick` (лише 10 тис. рахунків / 30 тис. операцій, не замінює повний експеримент).

Фактичні результати зберігаються в `benchmarks/results/` (CSV, профіль, графіки й параметри середовища). **Повний запуск на іншому ПК створить нові часи:** графіки та таблиця у звіті відображають виконання в середовищі підготовки, а не заміри на комп'ютері студента.

> Важливо: синтетичні значення представлені в цілих копійках. `balances` — поточні залишки, а `amounts` — окремий демонстраційний журнал обороту; підсумок залишків не виводиться з цього журналу. Живі рахунки через небезпечний race-condition приклад не змінюються.

> У початковому архіві залишались застарілі unit-тести, які імпортують відсутні після попередньої міграції до SQLAlchemy символи `BankAccount` і `InMemoryRepository`. Тому `pytest -q tests` (всі архівні тести) може завершитися помилкою колекції; штатний `python -m pytest -q` запускає актуальний інтеграційний набір і тести ЛР9, зазначені в `pyproject.toml`.
