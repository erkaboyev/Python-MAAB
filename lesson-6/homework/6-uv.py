# lesson6.py
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, List


# ============================================================
# Small helpers (robust console input for interactive section)
# ============================================================

def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """
    Read an integer with optional bounds. Re-prompts on invalid input.
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


# =========================
# Task 1. Modify String
# =========================
VOWELS = set("aeiouAEIOU")

def insert_underscores(txt: str) -> str:
    r"""
    Insert ‘_’ after every third character in the string.
    If the “target” character is a vowel OR the insertion falls on the last character,
    shift the insertion to the right (you can shift several times), do not put the ‘_’ sign at the end of the string.

    The algorithm is chosen to match the examples from the task.

    >>> insert_underscores("hello")
    'hel_lo'
    >>> insert_underscores("assalom")
    'ass_alom'
    >>> insert_underscores("abcabcabcdeabcdefabcdefg")
    'abc_abcab_cdeabcd_efabcdef_g'
    """
    if not txt:
        return txt

    res = []
    count = 0                   # count characters from the last insertion of '_'
    i = 0
    n = len(txt)

    while i < n:
        ch = txt[i]
        res.append(ch)
        count += 1

        if count == 3:
            # try to place ‘_’ after position i (and shift if necessary)
            j = i
            while True:
                # cannot be placed at the very end
                if j >= n - 1:
                    # skip this insert
                    break
                # Do not place after a vowel — move to the right
                if txt[j] in VOWELS:
                    j += 1
                    continue
                # also shift if the new position affects the vowel letter j+1
                # (this rule helps to match the reference example from the task)
                if txt[j + 1] in VOWELS:
                    j += 1
                    # but if after the shift we end up on a vowel, the cycle will continue shifting
                    continue
                # everything's fine — let's insert it
                res.append("_")
                # Reset the counter and continue processing from character i+1
                break
            count = 0
        i += 1

    # We do not add the final ‘_’ at the end according to the condition (we avoid it anyway).
    return "".join(res)


# ============================================
# Task 2. Integer Squares (0 <= i < n) print
# ============================================

def squares_0_to_n_minus_1(n: int) -> List[int]:
    """
    Return the list i^2 for i = 0..n-1 (printing makes it interactive).
    >>> squares_0_to_n_minus_1(5)
    [0, 1, 4, 9, 16]
    """
    return [i * i for i in range(n)]


# =========================
# Task 3. Loop-based Tasks
# =========================

def first_10_naturals() -> List[int]:
    """
    Exercise 1: Print first 10 natural numbers using while loop (вернём как список).
    >>> first_10_naturals()
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    i, out = 1, []
    while i <= 10:
        out.append(i)
        i += 1
    return out


def number_triangle(n: int = 5) -> List[List[int]]:
    """
    Exercise 2: Pattern
    1
    1 2
    ...
    1..n
    >>> number_triangle(5)
    [[1], [1, 2], [1, 2, 3], [1, 2, 3, 4], [1, 2, 3, 4, 5]]
    """
    return [list(range(1, row + 1)) for row in range(1, n + 1)]


def sum_1_to_n(n: int) -> int:
    """
    Exercise 3: Sum 1..n
    >>> sum_1_to_n(10)
    55
    """
    # Gauss's formula and/or loop; we use the formula
    return n * (n + 1) // 2


def multiplication_table(x: int, upto: int = 10) -> List[int]:
    """
    Exercise 4: Multiplication table for the number x: x*1..x*upto
    >>> multiplication_table(2)
    [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
    """
    return [x * i for i in range(1, upto + 1)]


def filtered_divisible_by_5(nums: Iterable[int]) -> List[int]:
    """
    Exercise 5:
    - print numbers that are multiples of 5
    - if the number is greater than 150, skip it
    - if the number is greater than 500, stop (break)
    >>> filtered_divisible_by_5([12, 75, 150, 180, 145, 525, 50])
    [75, 150, 145]
    """
    out: List[int] = []
    for v in nums:
        if v > 500:
            break
        if v > 150:
            continue
        if v % 5 == 0:
            out.append(v)
    return out


def count_digits(n: int) -> int:
    """
    Exercise 6: count digits in a number
    >>> count_digits(75869)
    5
    """
    return len(str(abs(n)))


def reverse_number_pattern(n: int = 5) -> List[List[int]]:
    """
    Exercise 7:
    5 4 3 2 1
    4 3 2 1
    ...
    1
    >>> reverse_number_pattern(5)
    [[5, 4, 3, 2, 1], [4, 3, 2, 1], [3, 2, 1], [2, 1], [1]]
    """
    return [list(range(row, 0, -1)) for row in range(n, 0, -1)]


def list_reversed(lst: List[int]) -> List[int]:
    """
    Exercise 8: print list in reverse order
    >>> list_reversed([10, 20, 30, 40, 50])
    [50, 40, 30, 20, 10]
    """
    # without cuts, you can go through the cycle from end to beginning
    out: List[int] = []
    for i in range(len(lst) - 1, -1, -1):
        out.append(lst[i])
    return out


def minus10_to_minus1() -> List[int]:
    """
    Exercise 9: -10..-1
    >>> minus10_to_minus1()
    [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1]
    """
    return list(range(-10, 0))


def numbers_with_done(n: int = 5) -> List[str]:
    """
    Exercise 10: print 0..n-1 and ‘Done!’ after the loop
    >>> numbers_with_done(5)
    ['0', '1', '2', '3', '4', 'Done!']
    """
    out = [str(i) for i in range(n)]
    out.append("Done!")
    return out


def is_prime(x: int) -> bool:
    """
    Simple prime number check (for small ranges).
    """
    if x < 2:
        return False
    if x in (2, 3):
        return True
    if x % 2 == 0:
        return False
    r = int(math.isqrt(x))
    for d in range(3, r + 1, 2):
        if x % d == 0:
            return False
    return True


def primes_between(a: int, b: int) -> List[int]:
    """
    Exercise 11: prime numbers in [a, b]
    >>> primes_between(25, 50)
    [29, 31, 37, 41, 43, 47]
    """
    lo, hi = min(a, b), max(a, b)
    return [x for x in range(lo, hi + 1) if is_prime(x)]


def fibonacci(n_terms: int) -> List[int]:
    """
    Exercise 12: Fibonacci up to n terms
    >>> fibonacci(10)
    [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    """
    if n_terms <= 0:
        return []
    if n_terms == 1:
        return [0]
    seq = [0, 1]
    while len(seq) < n_terms:
        seq.append(seq[-1] + seq[-2])
    return seq


def factorial(n: int) -> int:
    """
    Exercise 13: factorial
    >>> factorial(5)
    120
    >>> factorial(0)
    1
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res


# ==============================================
# Task 4. Uncommon elements of two lists (multiset)
# ==============================================

def uncommon_elements(list1: Iterable[int], list2: Iterable[int]) -> List[int]:
    """
    Return elements that are NOT common to both lists, taking into account multiplicity.
    The order is not important.

    Implemented using Counter: (c1 - c2) + (c2 - c1) — symmetric difference
    of multisets. See the documentation on Counter (bag/multiset) in the standard library.

    >>> uncommon_elements([1, 1, 2], [2, 3, 4])  # two “1”s remain, 2 is reduced, 3 and 4 are added
    [1, 1, 3, 4]
    >>> sorted(uncommon_elements([1, 2, 3], [4, 5, 6]))
    [1, 2, 3, 4, 5, 6]
    >>> sorted(uncommon_elements([1, 1, 2, 3, 4, 2], [1, 3, 4, 5]))
    [2, 2, 5]
    """
    c1, c2 = Counter(list1), Counter(list2)
    diff = (c1 - c2) + (c2 - c1)
    # unfold back into a list, repeating elements by their residual counters
    out: List[int] = []
    for k, cnt in diff.items():
        out.extend([k] * cnt)
    return out


# ======================
# Simple CLI for checks
# ======================

def _menu() -> None:
    print("=== Lesson 6 ===")
    print("1) Task 1 — Modify String with underscores")
    print("2) Task 2 — Integer Squares 0..n-1")
    print("3) Task 3 — Loop-based mini-exercises")
    print("4) Task 4 — Uncommon elements of two lists")
    print("0) Exit")

    while True:
        choice = read_int("Select an option: ", min_val=0, max_val=4)
        if choice == 0:
            print("Bye!")
            return

        if choice == 1:
            s = input("Enter a string: ")
            print(insert_underscores(s))

        elif choice == 2:
            n = read_int("Enter n (1..20): ", min_val=1, max_val=20)
            for val in squares_0_to_n_minus_1(n):
                print(val)

        elif choice == 3:
            print("--- Exercise 1: first 10 natural ---")
            print(first_10_naturals())

            print("\n--- Exercise 2: numerical triangle ---")
            for row in number_triangle(5):
                print(" ".join(map(str, row)))

            print("\n--- Exercise 3: sum 1..n ---")
            n = read_int("n: ", min_val=0)
            print(sum_1_to_n(n))

            print("\n--- Exercise 4: multiplication table ---")
            x = read_int("x: ")
            print(multiplication_table(x))

            print("\n--- Exercise 5: filter by conditions ---")
            nums = [12, 75, 150, 180, 145, 525, 50]
            print(filtered_divisible_by_5(nums))

            print("\n--- Exercise 6: number of digits ---")
            n = read_int("n: ")
            print(count_digits(n))

            print("\n--- Exercise 7: reverse pattern ---")
            for row in reverse_number_pattern(5):
                print(" ".join(map(str, row)))

            print("\n--- Exercise 8: reverse order listе ---")
            print(list_reversed([10, 20, 30, 40, 50]))

            print("\n--- Exercise 9: -10..-1 ---")
            print(minus10_to_minus1())

            print("\n--- Exercise 10: Done after cycle ---")
            print("\n".join(numbers_with_done(5)))

            print("\n--- Exercise 11: simple in range ---")
            a = read_int("from: ")
            b = read_int("to:   ")
            print(primes_between(a, b))

            print("\n--- Exercise 12: Fibonacci n terms ---")
            n = read_int("n_terms: ", min_val=0)
            print(fibonacci(n))

            print("\n--- Exercise 13: factorial ---")
            n = read_int("n (>=0): ", min_val=0)
            print(factorial(n))

        elif choice == 4:
            print("Enter the items in the first list separated by a space:")
            l1 = input().split()
            print("Enter the items in the second list separated by a space.:")
            l2 = input().split()
            # Let's try as numbers, then as strings
            try:
                l1n = [int(x) for x in l1]
                l2n = [int(x) for x in l2]
                print(uncommon_elements(l1n, l2n))
            except ValueError:
                print(uncommon_elements(l1, l2))

        print("-" * 40)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # running doc tests at startup
    _menu()
