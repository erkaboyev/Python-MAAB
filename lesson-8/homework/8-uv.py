# Lesson 8: Exceptions & File I/O
from __future__ import annotations

import os
import re
import random
import io
from collections import deque
from typing import Iterable, List, Dict

# =========================
# Small input helper (CLI)
# =========================
def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """Read an integer with optional bounds, re-prompting on errors."""
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
            if (min_val is not None and x < min_val) or (max_val is not None and x > max_val):
                lo = min_val if min_val is not None else "-inf"
                hi = max_val if max_val is not None else "+inf"
                print(f"Enter an integer in range [{lo}; {hi}]")
                continue
            return x
        except ValueError:
            print("Please enter a valid integer.")

# ======================================================
# Task 1 — Exception Handling (10 mini-exercises)
# ======================================================

# 1) ZeroDivisionError
def safe_divide(a: float, b: float) -> str:
    """
    Divide a by b with ZeroDivisionError handling.

    >>> safe_divide(10, 2)
    'Result: 5.0'
    >>> safe_divide(1, 0)
    'Error: division by zero'
    """
    try:
        return f"Result: {a / b}"
    except ZeroDivisionError:
        return "Error: division by zero"

# 2) Prompt int; raise ValueError if invalid
def parse_int_str(s: str) -> int:
    """
    Parse int or raise ValueError.

    >>> parse_int_str("42")
    42
    >>> parse_int_str("x")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: ...
    """
    s = s.strip()
    if not s or not re.fullmatch(r"[+-]?\d+", s):
        raise ValueError("Not a valid integer.")
    return int(s)

# 3) FileNotFoundError
def read_file_safe(path: str, encoding: str = "utf-8") -> str:
    """
    Open and read a file; handle FileNotFoundError.
    Returns content or error message.
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        return "Error: file not found"

# 4) Prompt two numbers; raise TypeError if not numeric
def add_numbers_str(a: str, b: str) -> float:
    """
    Convert two inputs to float and return their sum.
    Raise TypeError if conversion fails.

    >>> add_numbers_str("1.5", "2.5")
    4.0
    >>> add_numbers_str("x", "2")  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    TypeError: ...
    """
    try:
        return float(a) + float(b)
    except Exception as e:
        raise TypeError("Inputs must be numeric.") from e

# 5) PermissionError
def open_with_permission_check(path: str, mode: str = "r", encoding: str = "utf-8") -> str:
    """
    Try open a file and handle PermissionError if it occurs.
    """
    try:
        with open(path, mode, encoding=encoding) as f:
            return "Opened OK"
    except PermissionError:
        return "Error: permission denied"

# 6) IndexError
def list_get_safe(items: list, idx: int):
    """
    Safe list indexing with IndexError handling.

    >>> list_get_safe([1,2,3], 1)
    2
    >>> list_get_safe([1,2,3], 5)
    'Error: index out of range'
    """
    try:
        return items[idx]
    except IndexError:
        return "Error: index out of range"

# 7) KeyboardInterrupt
def prompt_number_keyboard_safe(prompt: str = "Enter a number: ") -> str:
    """
    Prompt a number; handle KeyboardInterrupt gracefully.
    Returns message instead of stacktrace.
    """
    try:
        s = input(prompt)
        _ = float(s)
        return "OK"
    except KeyboardInterrupt:
        return "Input cancelled by user (KeyboardInterrupt)"
    except ValueError:
        return "Not a number"

# 8) ArithmeticError (base for ZeroDivisionError, etc.)
def divide_arithmetic(a: float, b: float) -> str:
    """
    Division with catch-all ArithmeticError (covers ZeroDivisionError).

    >>> divide_arithmetic(4, 2)
    'Result: 2.0'
    >>> divide_arithmetic(1, 0)
    'Arithmetic error'
    """
    try:
        return f"Result: {a / b}"
    except ArithmeticError:   # parent for ZeroDivisionError, OverflowError, etc.
        return "Arithmetic error"

# 9) UnicodeDecodeError
def read_text_handle_unicode(path: str, encoding: str = "utf-8") -> str:
    """
    Read file; on UnicodeDecodeError try 'utf-8' with replacement.
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

# 10) AttributeError
def safe_getattr(obj, name: str, default: str = "Error: attribute not found"):
    """
    Get attribute or return default on AttributeError.

    >>> class A: pass
    >>> a = A(); a.x = 10
    >>> safe_getattr(a, "x")
    10
    >>> safe_getattr(a, "y")
    'Error: attribute not found'
    """
    try:
        return getattr(obj, name)
    except AttributeError:
        return default

# ======================================================
# Task 2 — File I/O (multiple exercises)
# All text operations use UTF-8 by default.
# ======================================================

# 1) Read entire text file
def read_all(path: str, encoding: str = "utf-8") -> str:
    """Return entire file content."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()

# 2) Read first n lines
def read_first_n_lines(path: str, n: int, encoding: str = "utf-8") -> List[str]:
    """Return first n lines (without trailing newlines)."""
    out: List[str] = []
    with open(path, "r", encoding=encoding) as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            out.append(line.rstrip("\n"))
    return out

# 3) Append text to a file and display it
def append_text_and_show(path: str, text: str, encoding: str = "utf-8") -> str:
    """Append text with newline if missing, then return new content."""
    if text and not text.endswith("\n"):
        text += "\n"
    with open(path, "a", encoding=encoding) as f:
        f.write(text)
    return read_all(path, encoding)

# 4) Read last n lines (efficient)
def read_last_n_lines(path: str, n: int, encoding: str = "utf-8") -> List[str]:
    """Return last n lines using deque."""
    dq: deque[str] = deque(maxlen=n)
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            dq.append(line.rstrip("\n"))
    return list(dq)

# 5) Read file line by line into a list
def lines_to_list(path: str, encoding: str = "utf-8") -> List[str]:
    """Return all lines stripped of trailing newlines."""
    with open(path, "r", encoding=encoding) as f:
        return [line.rstrip("\n") for line in f]

# 6) Read file line by line into a variable (single string)
def lines_to_string(path: str, encoding: str = "utf-8") -> str:
    """Return entire file as a single string (joined by newlines)."""
    return "\n".join(lines_to_list(path, encoding))

# 7) Read into an array (alias of list reading)
def lines_to_array(path: str, encoding: str = "utf-8") -> List[str]:
    """Alias for list of lines."""
    return lines_to_list(path, encoding)

# 8) Find the longest words
def longest_words(path: str, encoding: str = "utf-8") -> List[str]:
    """
    Return list of longest word(s) in file (alphanumeric words).
    """
    content = read_all(path, encoding)
    words = re.findall(r"[A-Za-z0-9']+", content)
    if not words:
        return []
    m = max(map(len, words))
    return sorted({w for w in words if len(w) == m})

# 9) Count number of lines
def count_lines(path: str, encoding: str = "utf-8") -> int:
    """Return count of lines in a file."""
    with open(path, "r", encoding=encoding) as f:
        return sum(1 for _ in f)

# 10) Word frequency
def word_frequency(path: str, encoding: str = "utf-8") -> Dict[str, int]:
    """
    Return dict word -> count (case-insensitive; split on non-letters/digits).
    """
    content = read_all(path, encoding).lower()
    words = re.findall(r"[a-z0-9']+", content)
    freq: Dict[str, int] = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq

# 11) File size (bytes)
def file_size(path: str) -> int:
    """
    Return file size in bytes.

    >>> isinstance(file_size.__doc__, str)
    True
    """
    return os.path.getsize(path)

# 12) Write a list to a file (one item per line)
def write_list(path: str, items: Iterable[str], encoding: str = "utf-8") -> None:
    """Write each item as a separate line."""
    with open(path, "w", encoding=encoding) as f:
        for it in items:
            f.write(f"{it}\n")

# 13) Copy contents from one file to another
def copy_file(src: str, dst: str, encoding: str = "utf-8") -> None:
    """Copy text file content preserving UTF-8."""
    with open(src, "r", encoding=encoding) as s, open(dst, "w", encoding=encoding) as d:
        for chunk in s:
            d.write(chunk)

# 14) Combine each line from file1 with corresponding line from file2
def combine_lines(file1: str, file2: str, sep: str = " | ", encoding: str = "utf-8") -> List[str]:
    """
    Combine corresponding lines (shorter file is padded with empty string).
    """
    a = lines_to_list(file1, encoding)
    b = lines_to_list(file2, encoding)
    L = max(len(a), len(b))
    out = []
    for i in range(L):
        s1 = a[i] if i < len(a) else ""
        s2 = b[i] if i < len(b) else ""
        out.append(f"{s1}{sep}{s2}")
    return out

# 15) Read a random line from a file
def random_line(path: str, encoding: str = "utf-8") -> str:
    """Return a random line (without trailing newline)."""
    lines = lines_to_list(path, encoding)
    return random.choice(lines) if lines else ""

# 16) Assess if a file is closed or not
def assess_closed(path: str, encoding: str = "utf-8") -> tuple[bool, bool]:
    """
    Open a file and return (closed_before, closed_after) for demonstration.
    """
    f = open(path, "r", encoding=encoding)
    before = f.closed
    _ = f.read(0)
    f.close()
    after = f.closed
    return before, after

# 17) Remove newline characters from a file
def read_without_newlines(path: str, encoding: str = "utf-8") -> List[str]:
    """Return lines with newline characters removed."""
    return lines_to_list(path, encoding)

# 18) Return number of words (commas are also separators)
def count_words(path: str, encoding: str = "utf-8") -> int:
    """
    Split by commas and whitespace: r'[\\s,]+'.
    >>> _tmp = "a,b c\\n d,,e"
    >>> len(re.split(r'[\\s,]+', _tmp.strip()))
    5
    """
    content = read_all(path, encoding).strip()
    if not content:
        return 0
    parts = re.split(r"[\s,]+", content)
    return sum(1 for p in parts if p)

# 19) Extract characters from various text files into a list
def characters_from_files(paths: Iterable[str], encoding: str = "utf-8") -> List[str]:
    """Concatenate all characters from the given files into a list."""
    chars: List[str] = []
    for p in paths:
        try:
            with open(p, "r", encoding=encoding) as f:
                chars.extend(list(f.read()))
        except FileNotFoundError:
            # Skip missing files; could also append a marker if desired
            continue
    return chars

# 20) Generate 26 files A.txt ... Z.txt
def generate_alpha_files(dir_path: str, content: str | None = None) -> List[str]:
    """
    Create A.txt..Z.txt in dir_path. If content is None, write the letter itself.
    Returns list of created file paths.
    """
    from string import ascii_uppercase
    created = []
    os.makedirs(dir_path, exist_ok=True)
    for ch in ascii_uppercase:
        path = os.path.join(dir_path, f"{ch}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content if content is not None else ch)
        created.append(path)
    return created

# 21) Create a file where all alphabet letters are listed with N per line
def write_alphabet_wrapped(path: str, per_line: int) -> None:
    """
    Write English alphabet with 'per_line' letters per line (A..Z).
    """
    from string import ascii_uppercase
    lines = [ascii_uppercase[i : i + per_line] for i in range(0, len(ascii_uppercase), per_line)]
    with open(path, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")

# ======================
# Minimal CLI
# ======================
def _menu() -> None:
    print("=== Lesson 8: Exceptions & File I/O ===")
    print("0) Exit")
    print("1) Exceptions demo")
    print("2) File I/O demo (read/write basic)")

    while True:
        choice = read_int("Choose: ", min_val=0, max_val=2)
        if choice == 0:
            print("Bye!")
            return

        if choice == 1:
            # quick interactive showcases
            print("-- ZeroDivisionError demo --")
            a = read_int("a: "); b = read_int("b: ")
            print(safe_divide(a, b))

            print("-- ValueError (parse int) demo --")
            s = input("Enter an integer: ")
            try:
                print(parse_int_str(s))
            except ValueError as e:
                print(f"Error: {e}")

            print("-- AttributeError demo --")
            class T: pass
            t = T(); t.v = 123
            print(safe_getattr(t, "v"), safe_getattr(t, "missing"))

        if choice == 2:
            # you can adapt paths for your local tests
            path = input("Enter path to a text file (it may be new): ").strip() or "sample.txt"
            print("-- append then show --")
            txt = input("Text to append: ")
            print(append_text_and_show(path, txt))

            print("-- last 3 lines --")
            print(read_last_n_lines(path, 3))

            print("-- longest words --")
            print(longest_words(path))

            print("-- word frequency (top few) --")
            freq = word_frequency(path)
            print(sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:5])

        print("-" * 40)

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    _menu()
