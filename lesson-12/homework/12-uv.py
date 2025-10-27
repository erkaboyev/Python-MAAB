# lesson12.py — Concurrency (threads) mini‑module
"""
This single file solves Lesson 12 homework with clean structure, doctests,
and an interactive CLI. It follows PEP 8/PEP 257 and past mentor feedback:
- precise exceptions (no silent failures),
- robust input readers,
- doctests (pytest-ready),
- concise comments in English,
- predictable, readable CLI demos.

⚠️ Note on design and performance
Threads in CPython are great for I/O-bound workloads (e.g., file reading).
For heavy CPU-bound work (e.g., primality test of huge ranges), the GIL limits
true parallel CPU usage. We still implement a *threaded* prime checker as
required by the assignment; for speed on CPU-bound tasks you would typically
prefer processes (ProcessPoolExecutor). The code below is structured so that
it is easy to switch the executor type if needed.

Run doctests:
    python lesson12.py --test

Start interactive CLI:
    python lesson12.py
"""
from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from math import isqrt
from pathlib import Path
from time import perf_counter
from typing import Iterable, List, Sequence, Tuple

import doctest
import queue
import re
import sys


# ──────────────────────────────────────────────────────────────────────────────
# Small utilities: robust input readers and pretty printing
# ──────────────────────────────────────────────────────────────────────────────

def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """Read an integer with validation loop (Ctrl+C to abort)."""
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
        except ValueError:
            print("Please enter a valid integer.")
            continue
        if (min_val is not None and x < min_val) or (max_val is not None and x > max_val):
            lo = min_val if min_val is not None else "-∞"
            hi = max_val if max_val is not None else "+∞"
            print(f"Please enter an integer in range [{lo}, {hi}].")
            continue
        return x


def read_path(prompt: str) -> Path:
    """Read a filesystem path that must exist and be a file."""
    while True:
        s = input(prompt).strip()
        p = Path(s)
        if p.is_file():
            return p
        print("File not found. Please enter a valid file path.")


def hr(title: str = "", width: int = 72) -> None:
    """Print a visual separator with an optional title."""
    print("\n" + ("=" * width))
    if title:
        print(title)
        print("-" * width)


# ──────────────────────────────────────────────────────────────────────────────
# Task 1 — Core number theory helpers (primality etc.)
# ──────────────────────────────────────────────────────────────────────────────

def is_prime(n: int) -> bool:
    """Return True if *n* is a prime number (n > 1), else False.

    The implementation uses trial division up to floor(sqrt(n)) and skips
    obvious composites quickly.

    >>> [x for x in range(1, 20) if is_prime(x)]
    [2, 3, 5, 7, 11, 13, 17, 19]
    >>> is_prime(2), is_prime(1), is_prime(25)
    (True, False, False)
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # Check numbers of the form 6k +/- 1 up to sqrt(n)
    limit = isqrt(n)
    f = 5
    while f <= limit:
        if n % f == 0 or n % (f + 2) == 0:
            return False
        f += 6
    return True


def split_range(lo: int, hi: int, parts: int) -> List[Tuple[int, int]]:
    """Split inclusive integer range [lo, hi] into *parts* nearly equal chunks.

    Returns a list of (start, end) pairs. Empty if hi < lo.

    >>> split_range(1, 10, 3)
    [(1, 4), (5, 7), (8, 10)]
    >>> split_range(5, 5, 4)
    [(5, 5)]
    >>> split_range(10, 1, 2)  # swapped automatically
    [(1, 5), (6, 10)]
    """
    if parts <= 0:
        raise ValueError("parts must be >= 1")
    if hi < lo:
        lo, hi = hi, lo
    if lo > hi:
        return []
    n = hi - lo + 1
    b, r = divmod(n, min(parts, n))  # base size and remainder
    out: List[Tuple[int, int]] = []
    start = lo
    for i in range(min(parts, n)):
        size = b + (1 if i < r else 0)
        end = start + size - 1
        out.append((start, end))
        start = end + 1
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Task 2 — Threaded Prime Number Checker
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class PrimeJob:
    start: int
    end: int


def _prime_worker(job: PrimeJob) -> List[int]:
    """Worker that returns primes in the inclusive subrange [start, end].

    Designed to be used with ThreadPoolExecutor.
    """
    return [n for n in range(job.start, job.end + 1) if is_prime(n)]


def threaded_primes(lo: int, hi: int, threads: int = 4) -> List[int]:
    """Find all prime numbers in [lo, hi] using *threads* workers.

    Returns primes sorted ascending.

    >>> threaded_primes(1, 30, threads=3)[:10]
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    if threads <= 0:
        raise ValueError("threads must be >= 1")
    ranges = [PrimeJob(a, b) for a, b in split_range(lo, hi, threads)]
    primes: List[int] = []
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(_prime_worker, job) for job in ranges]
        for fut in as_completed(futures):
            primes.extend(fut.result())
    primes.sort()
    return primes


# ──────────────────────────────────────────────────────────────────────────────
# Task 3 — Threaded File Processing: word frequency counter
# ──────────────────────────────────────────────────────────────────────────────

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def tokenize_to_words(text: str) -> list[str]:
    """Tokenize *text* to a list of lowercase "words" using ``\w+`` pattern.

    Unicode-aware and simple. Adjust the regex if you need other word rules.

    >>> tokenize_to_words("Hello, world! 1+1=2")
    ['hello', 'world', '1', '1', '2']
    >>> tokenize_to_words("O'Connor & co.")
    ['o', 'connor', 'co']
    """
    return [w.casefold() for w in _WORD_RE.findall(text)]


@dataclass(slots=True)
class WordCountConfig:
    threads: int = 4
    encoding: str = "utf-8"
    queue_maxsize: int = 10_000  # backpressure for producer


def _wordcount_worker(idx: int, q: "queue.Queue[str | None]", results: list[Counter]) -> None:
    """Consume lines from *q*, update a local Counter, then store in *results[idx]*.

    The queue carries strings (lines) and a sentinel ``None`` to signal the end.
    """
    local = Counter()
    while True:
        line = q.get()
        if line is None:
            q.task_done()
            break
        local.update(tokenize_to_words(line))
        q.task_done()
    results[idx] = local


def threaded_word_count(path: Path, cfg: WordCountConfig | None = None) -> Counter:
    """Count word occurrences in *path* using a pool of worker threads.

    The main thread streams the file line-by-line into a synchronized queue.
    Each worker thread consumes lines and builds a local Counter; then we merge
    results to the final Counter. This design avoids loading the whole file into
    memory and keeps updates mostly thread-local (fast).

    >>> from pathlib import Path
    >>> p = Path('._demo_l12.txt'); _ = p.write_text('One two TWO\nThree two!')
    >>> total = threaded_word_count(p, WordCountConfig(threads=2))
    >>> total['two'], total['three'], total['one']
    (3, 1, 1)
    """
    cfg = cfg or WordCountConfig()
    if cfg.threads <= 0:
        raise ValueError("threads must be >= 1")

    q: "queue.Queue[str | None]" = queue.Queue(maxsize=cfg.queue_maxsize)
    results: list[Counter] = [Counter() for _ in range(cfg.threads)]

    # Start workers
    import threading

    workers: list[threading.Thread] = []
    for i in range(cfg.threads):
        t = threading.Thread(target=_wordcount_worker, args=(i, q, results), daemon=True)
        t.start()
        workers.append(t)

    # Producer: stream lines into the queue
    with path.open("r", encoding=cfg.encoding, errors="ignore") as f:
        for line in f:
            q.put(line)

    # Send sentinels (one per worker), then wait for queue to drain
    for _ in range(cfg.threads):
        q.put(None)
    q.join()

    # Ensure workers exit cleanly
    for t in workers:
        t.join()

    # Merge local counters
    total = Counter()
    for c in results:
        total.update(c)
    return total


# ──────────────────────────────────────────────────────────────────────────────
# Task 4 — Interactive CLI demos for both exercises
# ──────────────────────────────────────────────────────────────────────────────

def demo_threaded_primes() -> None:
    """Interactive demo for the Threaded Prime Number Checker (Task 2)."""
    hr("Threaded Prime Number Checker (Task 2)")
    lo = read_int("Start of range: ")
    hi = read_int("End of range: ")
    threads = read_int("Threads (>=1): ", min_val=1)

    t0 = perf_counter()
    primes = threaded_primes(lo, hi, threads=threads)
    dt = perf_counter() - t0

    print(f"Found {len(primes)} primes in [{min(lo, hi)}, {max(lo, hi)}] using {threads} threads.")
    print("First primes:", primes[:20])
    if len(primes) > 20:
        print("… last primes:", primes[-10:])
    print(f"Elapsed: {dt:.3f} s")


def demo_threaded_wordcount() -> None:
    """Interactive demo for the Threaded File Processing (Task 3)."""
    hr("Threaded File Word Counter (Task 3)")
    path = read_path("Path to text file: ")
    threads = read_int("Threads (>=1): ", min_val=1)

    t0 = perf_counter()
    counts = threaded_word_count(path, WordCountConfig(threads=threads))
    dt = perf_counter() - t0

    # Show top‑N words
    top_n = 15
    print(f"Top {top_n} words:")
    for word, cnt in counts.most_common(top_n):
        print(f"  {word:>12s} : {cnt}")
    print(f"Unique words: {len(counts)}  —  Elapsed: {dt:.3f} s")


# ──────────────────────────────────────────────────────────────────────────────
# Test launcher and main menu
# ──────────────────────────────────────────────────────────────────────────────

def run_doctests(verbose: bool = False) -> Tuple[int, int]:
    """Run doctests for this module. Returns (failures, tests)."""
    return doctest.testmod(verbose=verbose)


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if "--test" in argv:
        fails, tests = run_doctests(verbose=False)
        msg = "All doctests passed!" if fails == 0 else f"{fails} of {tests} failed."
        print(msg)
        return 0 if fails == 0 else 1

    while True:
        hr("Lesson 12 — Threading Mini‑CLI")
        print("1) Task 2 — Threaded Prime Number Checker")
        print("2) Task 3 — Threaded File Word Counter")
        print("9) Run doctests")
        print("0) Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            demo_threaded_primes()
        elif choice == "2":
            demo_threaded_wordcount()
        elif choice == "9":
            fails, tests = run_doctests(verbose=True)
            print(f"\nSummary: {tests} tests, {fails} failures.")
        elif choice == "0":
            print("Bye!")
            return 0
        else:
            print(f"Invalid option '{choice}'. Please choose a number from the menu.")


if __name__ == "__main__":
    raise SystemExit(main())
