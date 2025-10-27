# lesson5.py
from __future__ import annotations
from typing import List, Tuple


# -------------------------------
# Helpers (input with basic validation)
# -------------------------------
def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
            if (min_val is not None and x < min_val) or (max_val is not None and x > max_val):
                rng = []
                if min_val is not None:
                    rng.append(str(min_val))
                if max_val is not None:
                    rng.append(str(max_val))
                print(f"Enter an integer in the range [{', '.join(rng)}].")
                continue
            return x
        except ValueError:
            print("Please enter an integer.")


# ===========================
# Task 1: Leap year function
# ===========================
def is_leap(year: int) -> bool:
    """
    Determine whether a given Gregorian year is a leap year.

    Rule (Gregorian calendar):
    - a year is a leap year if it is divisible by 4,
    - but not a leap year if it is also divisible by 100,
    - however, it is a leap year again if it is divisible by 400.

    >>> is_leap(2000)  # divided by 400
    True
    >>> is_leap(1900)  # divisible by 100, but not by 400
    False
    >>> is_leap(1996)  # divided by 4, not by 100
    True
    >>> is_leap(1999)
    False
    """
    if not isinstance(year, int):
        raise ValueError("Year must be an integer.")
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


# ==========================================
# Task 2: Conditional Statements ("Weird")
# ==========================================
def weird_or_not(n: int) -> str:
    """
    Rules:
    - if n is odd → “Weird”
    - if n is even and 2..5 → “Not Weird”
    - if n is even and 6..20 → “Weird”
    - if n is even and > 20 → “Not Weird”

    >>> weird_or_not(3)
    'Weird'
    >>> weird_or_not(4)
    'Not Weird'
    >>> weird_or_not(18)
    'Weird'
    >>> weird_or_not(24)
    'Not Weird'
    """
    if n % 2 == 1:
        return "Weird"
    if 2 <= n <= 5:
        return "Not Weird"
    if 6 <= n <= 20:
        return "Weird"
    return "Not Weird"


# =====================================================================
# Task 3: Even numbers between a and b (inclusive), no loops in logic
# =====================================================================

# Solution 1 (with if-else): correct parity with explicit branches
def evens_between_if(a: int, b: int) -> List[int]:
    """
    Return a list of even numbers in the range [a, b] inclusive.
    Implementation with if-else.

    >>> evens_between_if(1, 10)
    [2, 4, 6, 8, 10]
    >>> evens_between_if(2, 9)
    [2, 4, 6, 8]
    >>> evens_between_if(10, 1)  # the order of arguments is not important
    [2, 4, 6, 8, 10]
    >>> evens_between_if(5, 5)
    []
    """
    # guarantee that a <= b
    if a > b:
        a, b = b, a
    # adjust the boundaries to the nearest even numbers
    if a % 2 == 1:
        a += 1
    if b % 2 == 1:
        b -= 1
    # if the range is empty after adjustment, range will return an empty list
    return list(range(a, b + 1, 2)) if a <= b else []


# Solution 2 (without if-else): without if/elif/else — pure arithmetic + range
def evens_between_no_if(a: int, b: int) -> List[int]:
    """
    Return a list of even numbers in the range [a, b] inclusive.
    Without if/else: use boundary sorting and parity arithmetic.

    Idea: start = nearest even number >= min(a, b) → lo + (lo % 2)
          finish = nearest even number <= max(a, b) → hi - (hi % 2)
          range(start, finish+1, 2) will return [] if start > finish.

    >>> evens_between_no_if(1, 10)
    [2, 4, 6, 8, 10]
    >>> evens_between_no_if(10, 1)
    [2, 4, 6, 8, 10]
    >>> evens_between_no_if(5, 5)
    []
    >>> evens_between_no_if(2, 2)
    [2]
    """
    lo, hi = sorted((a, b))
    start = lo + (lo % 2)
    finish = hi - (hi % 2)
    return list(range(start, finish + 1, 2))


# -------------------------------
# interactive launch
# -------------------------------
def _menu() -> None:
    print("=== Lesson 5 ===")
    print("1) Task 1 — Leap year (is_leap)")
    print("2) Task 2 — Weird/Not Weird")
    print("3) Task 3 — Even numbers between a and b (two versions)")
    print("0) Exit")

    while True:
        choice = read_int("Select an item: ", min_val=0, max_val=3)
        if choice == 0:
            print("Bye!")
            return

        if choice == 1:
            y = read_int("Enter the year (int): ")
            try:
                print("Leap year?" , is_leap(y))
            except ValueError as e:
                print("Error:", e)

        elif choice == 2:
            n = read_int("Enter n (1..100): ", min_val=1, max_val=100)
            print(weird_or_not(n))

        elif choice == 3:
            a = read_int("Enter a: ")
            b = read_int("Enter b: ")
            print("Solution 1 (if-else):", evens_between_if(a, b))
            print("Solution 2 (no if):  ", evens_between_no_if(a, b))

        print("-" * 40)


if __name__ == "__main__":
    # Automatic launch of doctests when directly launching the file
    import doctest
    doctest.testmod(verbose=True)
    # then open the menu
    _menu()
