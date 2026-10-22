import pytest
from bank_system.performance_analytics import (generate_dataset, statistics_python, statistics_numpy,
    history_balance_python, CachedAccountAnalytics, account_turnover_python)
from bank_system.parallel import (summarize_chunk, aggregate_processes, aggregate_threads,
    SafeBankAccount, race_condition_example, manual_threads_example, manual_multiprocessing_example)

@pytest.fixture(scope='module')
def data():
    return generate_dataset(100, 500)

def test_python_numpy_identical(data):
    assert statistics_python(data) == statistics_numpy(data)

def test_thread_pool_matches(data):
    assert aggregate_threads(data.amounts, 2) == summarize_chunk(data.amounts)

def test_process_pool_matches(data):
    assert aggregate_processes(data.amounts, 2) == summarize_chunk(data.amounts)

def test_raw_multiprocessing(data):
    assert manual_multiprocessing_example(data.amounts) == sum(map(abs, data.amounts))

def test_manual_threads(data):
    assert manual_threads_example(data.amounts) == len(data.amounts)

def test_cache_invalidation(data):
    account_id = data.account_ids[0]
    cache = CachedAccountAnalytics(data.account_ids, data.amounts)
    before = account_turnover_python(data.account_ids, data.amounts, account_id)
    assert cache.turnover(account_id) == before
    assert cache.turnover(account_id) == before
    assert cache.turnover.cache_info().hits >= 1
    cache.add_transaction(account_id, -200)
    assert cache.turnover(account_id) == before + 200

def test_synchronization():
    account = SafeBankAccount(100)
    assert account.withdraw(90)
    assert not account.withdraw(20)
    account.deposit(50)
    assert account.balance == 60
    with pytest.raises(ValueError): account.deposit(-10)
    unsafe, safe = race_condition_example(4, 30)
    assert safe == 120
    assert unsafe <= safe

def test_no_negative_balance():
    assert history_balance_python(100, (-50, 30, -80)) == 0
    with pytest.raises(ValueError): history_balance_python(10, (-11,))

def test_reproducibility():
    assert generate_dataset(20, 30, 5) == generate_dataset(20, 30, 5)
