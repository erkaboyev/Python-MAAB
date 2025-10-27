# lesson7.py
from __future__ import annotations

import math
from typing import Iterable, List


# ===========================================================================
# Cheat sheet: examples of map / filter / lambda (for demonstration purposes)
# ===========================================================================

def map_filter_examples() -> dict[str, list]:
    """
    A small set of examples of using map/filter + lambda.

    >>> ex = map_filter_examples()
    >>> ex["squares"]
    [1, 4, 9, 16]
    >>> ex["sum_two_lists"]
    [11, 22, 33]
    >>> ex["only_even"]
    [2, 4, 6]
    """
    data = [1, 2, 3, 4]

    # map: squaring
    squares = list(map(lambda x: x * x, data))

    # map with two iterables: element-wise sum
    a, b = [1, 2, 3], [10, 20, 30]
    sum_two_lists = list(map(lambda x, y: x + y, a, b))

    # filter: keep even numbers
    only_even = list(filter(lambda x: x % 2 == 0, data))

    return {
        "squares": squares,
        "sum_two_lists": sum_two_lists,
        "only_even": only_even,
    }


# ==================================
# Helper: accurate input of integers
# ==================================

def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """
    Simple input of integers with optional boundaries.
    """
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
            if (min_val is not None and x < min_val) or (max_val is not None and x > max_val):
                lo = min_val if min_val is not None else "-inf"
                hi = max_val if max_val is not None else "+inf"
                print(f"Enter an integer in the range [{lo}; {hi}].")
                continue
            return x
        except ValueError:
            print("Please enter an integer.")


# =======================
# Task 1: is_prime(n)
# =======================

def is_prime(n: int) -> bool:
    """
    Returns True if n is a prime number (n > 1), otherwise False.

    Optimization: it is sufficient to check divisors up to floor(sqrt(n)).
    Python has an integer root `math.isqrt(n)`, which
    returns ⌊√n⌋ without floating point errors. :contentReference[oaicite:5]{index=5}
    
    >>> is_prime(4)
    False
    >>> is_prime(7)
    True
    >>> is_prime(1)
    False
    >>> is_prime(2)
    True
    >>> is_prime(49)
    False
    """
    if n <= 1:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = math.isqrt(n)  # integer root (>=0) — see documentation for math.isqrt
    for d in range(3, limit + 1, 2):
        if n % d == 0:
            return False
    return True


# ==========================
# Task 2: digit_sum(k)
# ==========================

def digit_sum(k: int) -> int:
    """
    The sum of the digits of the number k (ignoring the sign).

    Here we show an idiomatic solution using map+int:
    we convert string digits into numbers and sum them up.

    >>> digit_sum(24)   # 2 + 4
    6
    >>> digit_sum(502)  # 5 + 0 + 2
    7
    >>> digit_sum(-123)
    6
    """
    return sum(map(int, str(abs(k))))


# ============================================
# Task 3: 2**k <= N — output all powers of 2
# ============================================

def powers_of_two_upto(n: int) -> list[int]:
    """
    Return all numbers of the form 2**k that do not exceed n (k >= 1).
    Following the example from task 1, we do not include (2**0=1).

    Carefully and without errors with float logarithms:
    use the integer property: n.bit_length() - 1 = floor(log2(n))
    for n>0, which means k_max = n.bit_length() - 1. :contentReference[oaicite:6]{index=6}

    >>> powers_of_two_upto(10)
    [2, 4, 8]
    >>> powers_of_two_upto(1)
    []
    >>> powers_of_two_upto(2)
    [2]
    >>> powers_of_two_upto(16)
    [2, 4, 8, 16]
    """
    if n < 2:
        return []
    k_max = n.bit_length() - 1  # maximum degree (floor(log2(n)))
    return [1 << k for k in range(1, k_max + 1)]  # 1<<k == 2**k


# ======================
# Simple CLI menu
# ======================

def _menu() -> None:
    print("=== Lesson 7 ===")
    print("0) Exit")
    print("1) Examples map / filter / lambda")
    print("2) Task 1 — is_prime(n)")
    print("3) Task 2 — digit_sum(k)")
    print("4) Task 3 — degree pairs ≤ N")

    while True:
        choice = read_int("Select an item: ", min_val=0, max_val=4)
        if choice == 0:
            print("Bye!")
            return

        if choice == 1:
            ex = map_filter_examples()
            print("squares (map):       ", ex["squares"])
            print("sum_two_lists (map): ", ex["sum_two_lists"])
            print("only_even (filter):  ", ex["only_even"])

        elif choice == 2:
            n = read_int("Enter n (>0): ", min_val=1)
            print(is_prime(n))

        elif choice == 3:
            k = read_int("Enter k (may be negative): ")
            print(digit_sum(k))

        elif choice == 4:
            N = read_int("Enter N: ")
            res = powers_of_two_upto(N)
            # output in the format from the example
            if res:
                print(*res)
            else:
                print("(пусто)")

        print("-" * 40)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # auto-run examples
    _menu()
