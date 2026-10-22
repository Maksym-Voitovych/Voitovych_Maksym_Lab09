"""ЛР9: threads, processes, executors та синхронізація."""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from threading import Thread, Lock
from multiprocessing import Process, Queue
from time import sleep


def summarize_chunk(values: tuple[int, ...]) -> tuple[int, int, int, int]:
    incoming = outgoing = deposits = withdrawals = 0
    for amount in values:
        if amount >= 0:
            incoming += amount
            deposits += 1
        else:
            outgoing -= amount
            withdrawals += 1
    return incoming, outgoing, deposits, withdrawals


def chunks(values: tuple[int, ...], pieces: int) -> list[tuple[int, ...]]:
    size = max(1, (len(values) + pieces - 1) // pieces)
    return [values[pos:pos + size] for pos in range(0, len(values), size)]


def aggregate_processes(values: tuple[int, ...], workers: int = 4) -> tuple[int, int, int, int]:
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(summarize_chunk, chunks(values, workers * 4)))
    return tuple(sum(row[i] for row in results) for i in range(4))


def aggregate_threads(values: tuple[int, ...], workers: int = 4) -> tuple[int, int, int, int]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(summarize_chunk, chunks(values, workers * 4)))
    return tuple(sum(row[i] for row in results) for i in range(4))


def _read_log(path: str) -> tuple[int, int]:
    with open(path, encoding='utf-8') as stream:
        lines = stream.readlines()
    return len(lines), sum(int(line.strip().split(',')[1]) for line in lines)


def load_logs_sequential(paths: list[str]) -> list[tuple[int, int]]:
    return [_read_log(path) for path in paths]


def load_logs_threads(paths: list[str], workers: int = 4) -> list[tuple[int, int]]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_read_log, paths))


def manual_threads_example(values: tuple[int, ...]) -> int:
    lock = Lock()
    counter = [0]
    def worker(part: tuple[int, ...]) -> None:
        count = len(part)
        with lock:
            counter[0] += count
    threads = [Thread(target=worker, args=(part,)) for part in chunks(values, 4)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    return counter[0]


def _process_worker(values: tuple[int, ...], queue: Queue) -> None:
    queue.put(sum(abs(amount) for amount in values))


def manual_multiprocessing_example(values: tuple[int, ...]) -> int:
    """Окремі Process з Queue; викликати під if __name__ == '__main__' на Windows."""
    queue = Queue()
    parts = chunks(values, 2)
    processes = [Process(target=_process_worker, args=(part, queue)) for part in parts]
    for process in processes: process.start()
    result = sum(queue.get() for _ in processes)
    for process in processes: process.join()
    if any(process.exitcode != 0 for process in processes):
        raise RuntimeError('Помилка дочірнього процесу')
    queue.close()
    return result


class SafeBankAccount:
    def __init__(self, balance: int):
        if balance < 0: raise ValueError('Від’ємний баланс')
        self.balance = balance
        self.lock = Lock()

    def deposit(self, amount: int) -> None:
        if amount <= 0: raise ValueError('Сума має бути додатною')
        with self.lock:
            self.balance += amount

    def withdraw(self, amount: int) -> bool:
        if amount <= 0: raise ValueError('Сума має бути додатною')
        with self.lock:
            if self.balance < amount: return False
            self.balance -= amount
            return True


def race_condition_example(workers: int = 8, iterations: int = 100) -> tuple[int, int]:
    """Навмисно небезпечне read/write з yield, поряд — результат із Lock."""
    unsafe = [0]
    safe = [0]
    lock = Lock()
    def update() -> None:
        for _ in range(iterations):
            old = unsafe[0]
            sleep(0)  # примусове перемикання, демонстрація lost update
            unsafe[0] = old + 1
            with lock:
                safe[0] += 1
    jobs = [Thread(target=update) for _ in range(workers)]
    for job in jobs: job.start()
    for job in jobs: job.join()
    assert safe[0] == workers * iterations
    return unsafe[0], safe[0]
