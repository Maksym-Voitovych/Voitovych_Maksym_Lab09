"""Запуск: python benchmarks/benchmark_lab9.py [--quick]."""
from __future__ import annotations
import argparse
import cProfile
import csv
import io
import json
import os
from pathlib import Path
import pstats
import statistics
import sys
import tempfile
from time import perf_counter
import timeit
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bank_system.performance_analytics import (generate_dataset, statistics_python,
    statistics_numpy, CachedAccountAnalytics, account_turnover_python)
from bank_system.parallel import (aggregate_processes, aggregate_threads, summarize_chunk,
    load_logs_sequential, load_logs_threads, race_condition_example,
    manual_threads_example, manual_multiprocessing_example, SafeBankAccount)

OUTPUT = ROOT / 'benchmarks' / 'results'
OUTPUT.mkdir(parents=True, exist_ok=True)


def measure(function, repeats=5):
    times = []
    result = None
    for _ in range(repeats):
        start = perf_counter()
        result = function()
        times.append(perf_counter() - start)
    return statistics.median(times), result


def measure_memory(function):
    tracemalloc.start()
    function()
    _, peak = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    tracemalloc.stop()
    return peak / 1048576, snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Скорочений запуск для перевірки')
    args = parser.parse_args()
    n = 10_000 if args.quick else 100_000
    t = 30_000 if args.quick else 500_000
    repeats = 3 if args.quick else 5
    data = generate_dataset(n, t)
    print(f'Рахунків: {n}; транзакцій: {t}; повторів: {repeats}')
    expected = statistics_python(data)
    assert statistics_numpy(data) == expected
    target = (expected['incoming'], expected['outgoing'], expected['deposits'], expected['withdrawals'])
    assert summarize_chunk(data.amounts) == target
    rows = []
    def record(label, workload, workers, function, baseline=None, memory=False):
        median, result = measure(function, repeats)
        if memory:
            peak, _ = measure_memory(function)
        else:
            peak = None
        speedup = baseline / median if baseline is not None and median > 0 else 1.
        rows.append({'experiment': label, 'data_size': workload, 'workers': workers,
                     'median_seconds': round(median, 7), 'peak_memory_mb':
                      round(peak, 4) if peak is not None else '',
                     'speedup': round(speedup, 3)})
        print(f'{label:29} {median:10.6f} s | x{speedup:.2f}' +
              (f' | peak={peak:.2f} MB' if peak is not None else ''))
        return median, result

    base, result = record('Python baseline', t, 1, lambda: statistics_python(data), memory=True)
    assert result == expected
    _, result = record('NumPy vectorization', t, 1, lambda: statistics_numpy(data), base, True)
    assert result == expected
    chunk_base, result = record('Python turnover only', t, 1,
                                lambda: summarize_chunk(data.amounts), memory=True)
    assert result == target
    for workers in [1, 2, 4, 8]:
        _, result = record('ThreadPool CPU', t, workers,
                           lambda w=workers: aggregate_threads(data.amounts, w), chunk_base)
        assert result == target
        _, result = record('ProcessPool CPU', t, workers,
                           lambda w=workers: aggregate_processes(data.amounts, w), chunk_base)
        assert result == target
    # Вимірювання двох незалежних демонстрацій API
    assert manual_threads_example(data.amounts) == t
    assert manual_multiprocessing_example(data.amounts) == expected['turnover']
    # I/O на диску. ОС може кешувати файли, тому прискорення НЕ гарантоване.
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        block = data.amounts[:min(t, 12_000)]
        for i in range(8):
            path = Path(tmp) / f'operations_{i}.csv'
            with path.open('w', encoding='utf-8') as f:
                f.writelines(f'{j},{value}\n' for j, value in enumerate(block))
            paths.append(str(path))
        io_base, reference = record('Sequential CSV reading', len(paths), 1,
                                    lambda: load_logs_sequential(paths))
        _, result = record('ThreadPool CSV reading', len(paths), 4,
                            lambda: load_logs_threads(paths, 4), io_base)
        assert result == reference
    # Повторювана статистика конкретного рахунку: порівняння uncached vs cached.
    acc = data.account_ids[0]
    cached = CachedAccountAnalytics(data.account_ids, data.amounts)
    wanted = account_turnover_python(data.account_ids, data.amounts, acc)
    assert cached.turnover(acc) == wanted
    uncached_time, _ = record('Uncached repeated lookup', t, 1,
                              lambda: [account_turnover_python(data.account_ids, data.amounts, acc)
                                       for _ in range(20)])
    cached_time, _ = record('Cached repeated lookup', t, 1,
                            lambda: [cached.turnover(acc) for _ in range(20)], uncached_time)
    before = cached.turnover(acc)
    cached.add_transaction(acc, 12345)
    assert cached.turnover(acc) == before + 12345
    print('Cache invalidation: OK; info:', cached.turnover.cache_info())
    print('Race condition unsafe/safe:', race_condition_example())
    bank = SafeBankAccount(1000)
    assert bank.withdraw(250) and not bank.withdraw(1000)
    bank.deposit(250)
    assert bank.balance == 1000
    print('timeit, 100 warm cached reads:', timeit.timeit(lambda: cached.turnover(acc), number=100))
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(3): statistics_python(data)
    profiler.disable()
    profiler.dump_stats(str(OUTPUT / 'baseline.prof'))
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats('cumulative').print_stats(20)
    (OUTPUT / 'cprofile.txt').write_text(stream.getvalue(), encoding='utf-8')
    _, snapshot = measure_memory(lambda: statistics_python(data))
    (OUTPUT / 'tracemalloc.txt').write_text('\n'.join(map(str, snapshot.statistics('lineno')[:10])), encoding='utf-8')
    with (OUTPUT / 'benchmark_results.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {'python': sys.version, 'platform': sys.platform, 'logical_cpus': os.cpu_count(),
                'accounts': n, 'transactions': t, 'repeats': repeats,
                'note': 'Часи фактичні для поточного середовища; CPU/I/O заміри не однакове навантаження'}
    (OUTPUT / 'environment.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        def plot(data_rows, filename, title, field, ylabel):
            fig, ax = plt.subplots(figsize=(10, 5))
            labels = [r['experiment'] + (f" ({r['workers']})" if r['workers'] != 1 else '') for r in data_rows]
            ax.barh(labels, [r[field] for r in data_rows]); ax.invert_yaxis()
            ax.set(title=title, xlabel=ylabel)
            fig.tight_layout(); fig.savefig(OUTPUT / filename, dpi=160); plt.close(fig)
        cpu = [r for r in rows if r['experiment'] in
               ('Python turnover only', 'ThreadPool CPU', 'ProcessPool CPU')]
        plot(cpu, 'execution_time.png', 'CPU: time by workers', 'median_seconds', 'Seconds')
        plot(cpu, 'speedup.png', 'CPU: speedup relative to sequential', 'speedup', 'Speedup x')
        plot(rows[:2], 'numpy_comparison.png', 'Statistics: Python vs NumPy', 'median_seconds', 'Seconds')
    except ImportError:
        print('matplotlib відсутній: таблиці збережені, графіки пропущено.')
    print('Результати збережено:', OUTPUT)

if __name__ == '__main__':
    main()
