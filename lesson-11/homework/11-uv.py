# lesson11.py — Single-file solution that scaffolds custom modules/packages, runs doctests,
# shows virtualenv instructions, and provides interactive demos.

"""
Project goals
-------------
Task 1 — Create custom modules:
    - math_operations.py:
        add(a, b), subtract(a, b), multiply(a, b), divide(a, b)
    - string_utils.py:
        reverse_string(s), count_vowels(s)

Task 2 — Create custom packages:
    - geometry/
        __init__.py (exposes circle)
        circle.py (calculate_area(radius), calculate_circumference(radius))
    - file_operations/
        __init__.py (exposes file_reader, file_writer)
        file_reader.py (read_file(file_path))
        file_writer.py (write_file(file_path, content))

Also:
    - Interactive CLI (friendly messages, retry loops)
    - Doctests (doctest/testmod runner with a neat summary table)
    - Clear educational docstrings
    - Virtual environment “how-to” guide with best practices

All comments are in English, as requested.
"""

from __future__ import annotations

import importlib
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


# ───────────────────────────────────────────────────────────────────────────────
# Small utilities (formatting, path mgmt, reload import)
# ───────────────────────────────────────────────────────────────────────────────

def hr(title: str = "", char: str = "─", width: int = 60) -> None:
    """Print a horizontal rule with an optional centered title."""
    if title:
        pad = max(0, (width - len(title) - 2) // 2)
        print(char * pad, title, char * pad)
    else:
        print(char * width)


def add_sys_path_once(p: Path) -> None:
    """Add absolute path to sys.path once if not already present."""
    resolved = str(p.resolve())
    if resolved not in sys.path:
        sys.path.insert(0, resolved)


def import_fresh(module_name: str):
    """
    Import module (reloading if already imported). Helpful when files were just created.

    Returns the imported module object, or raises ImportError if something goes wrong.
    """
    if module_name in sys.modules:
        return importlib.reload(sys.modules[module_name])
    return importlib.import_module(module_name)


# ───────────────────────────────────────────────────────────────────────────────
# Task: Scaffolding — write modules/packages to disk
# ───────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class ScaffoldResult:
    base_dir: Path
    created_files: Tuple[Path, ...]


def create_scaffold(base_dir: Path) -> ScaffoldResult:
    """
    Create all requested modules and packages (if they don't exist), with rich docstrings
    and doctests. Idempotent: re-creating will overwrite files’ content deterministically.
    """
    base_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []

    # ------------------- math_operations.py -------------------
    (base_dir / "math_operations.py").write_text(textwrap.dedent("""\
        \"\"\"Basic arithmetic operations module.

        This module provides four fundamental arithmetic operations:
        addition, subtraction, multiplication, and division.

        All functions accept numeric types (int, float, or any type supporting
        __float__) and return float results for consistency.

        Key features:
            • Type-safe with SupportsFloat protocol
            • Division handles zero-divisor correctly (raises ZeroDivisionError)
            • Comprehensive doctests for validation

        Usage example:
            >>> import math_operations as mo
            >>> mo.add(10, 5)
            15.0
            >>> mo.divide(10, 2)
            5.0

        See also:
            • Python's built-in 'operator' module for more operations
            • 'decimal' module for precise decimal arithmetic
            • 'fractions' module for rational number arithmetic
        \"\"\"
        from __future__ import annotations
        from typing import SupportsFloat

        Number = SupportsFloat  # Any numeric type convertible to float

        def add(a: Number, b: Number) -> float:
            \"\"\"Add two numbers and return float.

            Examples:
                >>> add(2, 3)
                5.0
                >>> add(-10, 5)
                -5.0
                >>> add(1.5, 2.5)
                4.0
            \"\"\"
            return float(a) + float(b)

        def subtract(a: Number, b: Number) -> float:
            \"\"\"Subtract b from a and return float.

            Examples:
                >>> subtract(10, 4)
                6.0
                >>> subtract(5, 10)
                -5.0
                >>> subtract(0, 0)
                0.0
            \"\"\"
            return float(a) - float(b)

        def multiply(a: Number, b: Number) -> float:
            \"\"\"Multiply two numbers and return float.

            Examples:
                >>> multiply(1.5, 4)
                6.0
                >>> multiply(-3, 5)
                -15.0
                >>> multiply(0, 100)
                0.0
            \"\"\"
            return float(a) * float(b)

        def divide(a: Number, b: Number) -> float:
            \"\"\"Divide a by b, raising ZeroDivisionError if b == 0.

            Examples:
                >>> divide(8, 2)
                4.0
                >>> divide(7, 2)
                3.5
                >>> divide(-10, 5)
                -2.0
                >>> divide(1, 0)  # doctest: +IGNORE_EXCEPTION_DETAIL
                Traceback (most recent call last):
                ZeroDivisionError: division by zero
            \"\"\"
            return float(a) / float(b)

        if __name__ == "__main__":
            import doctest
            print("Running doctests for math_operations module...")
            failures, tests = doctest.testmod(verbose=True)
            if failures == 0:
                print(f"\\n✓ All {tests} tests passed!")
            else:
                print(f"\\n❌ {failures} out of {tests} tests failed.")
        """), encoding="utf-8")
    created.append(base_dir / "math_operations.py")

    # ------------------- string_utils.py -------------------
    (base_dir / "string_utils.py").write_text(textwrap.dedent("""\
        \"\"\"String utilities.

        Functions:
            - reverse_string(s): returns reversed copy of s
            - count_vowels(s): counts vowels (a, e, i, o, u) case-insensitively

        Examples:
            >>> reverse_string("Hello")
            'olleH'
            >>> count_vowels("AeiOuxYz")
            5
        \"\"\"
        from __future__ import annotations

        VOWELS = set("aeiou")

        def reverse_string(s: str) -> str:
            \"\"\"Return reversed string.

            >>> reverse_string("")
            ''
            >>> reverse_string("abc")
            'cba'
            \"\"\"
            return s[::-1]

        def count_vowels(s: str) -> int:
            \"\"\"Count vowels a/e/i/o/u (case-insensitive).

            >>> count_vowels("sky")
            0
            >>> count_vowels("Education")
            5
            >>> count_vowels("AEIOU")
            5
            \"\"\"
            return sum(1 for ch in s.lower() if ch in VOWELS)
        """), encoding="utf-8")
    created.append(base_dir / "string_utils.py")

    # ------------------- geometry package -------------------
    (base_dir / "geometry").mkdir(exist_ok=True)
    (base_dir / "geometry" / "__init__.py").write_text(textwrap.dedent("""\
        \"\"\"Geometry package.

        Currently exposes:
            - circle (module with area/circumference functions)
        \"\"\"
        from . import circle  # re-export for convenience

        __all__ = ["circle"]
        """), encoding="utf-8")
    created.append(base_dir / "geometry" / "__init__.py")

    (base_dir / "geometry" / "circle.py").write_text(textwrap.dedent("""\
        \"\"\"Circle calculations.

        Functions:
            - calculate_area(radius): πr²
            - calculate_circumference(radius): 2πr

        Radius must be non-negative.

        Examples:
            >>> calculate_area(0)
            0.0
            >>> round(calculate_area(1), 4)
            3.1416
            >>> round(calculate_circumference(1), 4)
            6.2832
            >>> calculate_area(-1)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            ValueError: radius must be non-negative
        \"\"\"
        from __future__ import annotations
        import math

        def _validate_radius(radius: float) -> None:
            if radius < 0:
                raise ValueError("radius must be non-negative")

        def calculate_area(radius: float) -> float:
            \"\"\"Return area of circle πr² as float.\"\"\"
            _validate_radius(radius)
            return math.pi * (radius ** 2)

        def calculate_circumference(radius: float) -> float:
            \"\"\"Return circumference of circle 2πr as float.\"\"\"
            _validate_radius(radius)
            return 2.0 * math.pi * radius
        """), encoding="utf-8")
    created.append(base_dir / "geometry" / "circle.py")

    # ------------------- file_operations package -------------------
    (base_dir / "file_operations").mkdir(exist_ok=True)
    (base_dir / "file_operations" / "__init__.py").write_text(textwrap.dedent("""\
        \"\"\"file_operations package.

        Exposes:
            - file_reader.read_file(path)
            - file_writer.write_file(path, content)
        \"\"\"
        from . import file_reader, file_writer

        __all__ = ["file_reader", "file_writer"]
        """), encoding="utf-8")
    created.append(base_dir / "file_operations" / "__init__.py")

    (base_dir / "file_operations" / "file_reader.py").write_text(textwrap.dedent("""\
        \"\"\"Simple file reader.

        read_file(file_path) -> str
            Reads entire text file (utf-8). Raises FileNotFoundError if not found.

        Examples:
            >>> from pathlib import Path
            >>> p = Path('tmp_read.txt')
            >>> _ = p.write_text('Hello!\\n', encoding='utf-8')
            >>> read_file(p).strip()
            'Hello!'
            >>> p.unlink()
            >>> read_file(p)  # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            FileNotFoundError: ...
        \"\"\"
        from __future__ import annotations
        from pathlib import Path

        def read_file(file_path: Path | str) -> str:
            p = Path(file_path)
            # Will raise FileNotFoundError naturally if missing:
            return p.read_text(encoding='utf-8')
        """), encoding="utf-8")
    created.append(base_dir / "file_operations" / "file_reader.py")

    (base_dir / "file_operations" / "file_writer.py").write_text(textwrap.dedent("""\
        \"\"\"Simple file writer.

        write_file(file_path, content) -> int
            Writes 'content' (str) to file (utf-8). Returns number of characters.

        Examples:
            >>> from pathlib import Path
            >>> p = Path('tmp_write.txt')
            >>> write_file(p, 'ABC\\n')
            4
            >>> p.read_text(encoding='utf-8')
            'ABC\\n'
            >>> p.unlink()
        \"\"\"
        from __future__ import annotations
        from pathlib import Path

        def write_file(file_path: Path | str, content: str) -> int:
            p = Path(file_path)
            p.write_text(content, encoding='utf-8')
            return len(content)
        """), encoding="utf-8")
    created.append(base_dir / "file_operations" / "file_writer.py")

    return ScaffoldResult(base_dir=base_dir, created_files=tuple(created))


# ───────────────────────────────────────────────────────────────────────────────
# Task: Doctest runner with friendly summary
# ───────────────────────────────────────────────────────────────────────────────

def run_created_doctests(base_dir: Path) -> None:
    """
    Import each created module and run doctest.testmod on it.
    Prints a detailed summary with visual indicators for pass/fail.
    """
    import doctest

    add_sys_path_once(base_dir)

    modules = [
        ("math_operations", "Math Operations"),
        ("string_utils", "String Utilities"),
        ("geometry.circle", "Geometry / Circle"),
        ("file_operations.file_reader", "File Reader"),
        ("file_operations.file_writer", "File Writer"),
    ]

    hr("Running Doctests")
    print("Testing all created modules and packages...\n")

    total_failed = 0
    total_attempted = 0
    results: list[tuple[str, str, int, int]] = []

    for module_name, display_name in modules:
        try:
            mod = import_fresh(module_name)
            failed, attempted = doctest.testmod(mod, verbose=False)

            status = "✓ PASS" if failed == 0 else f"❌ FAIL ({failed} failures)"
            results.append((display_name, status, attempted, failed))

            total_failed += failed
            total_attempted += attempted

        except Exception as e:
            results.append((display_name, f"❌ ERROR: {e}", 0, 0))

    # Print formatted results table
    print(f"{'Module':<30} {'Status':<20} {'Tests':<10}")
    print("-" * 60)
    for name, status, attempted, _failed in results:
        print(f"{name:<30} {status:<20} {attempted:<10}")

    # Summary
    hr("Summary")
    if total_failed == 0:
        print(f"🎉 Excellent! All {total_attempted} tests passed across all modules.")
        print("Your code is working correctly!")
    else:
        print(f"⚠ {total_failed} out of {total_attempted} tests failed.")
        print("Review the failures above and fix the issues in your code.")
        print("\nTip: Run individual module doctests with:")
        print("  python -m doctest -v <module_name>.py")


# ───────────────────────────────────────────────────────────────────────────────
# Task: Virtual environment guide (improved)
# ───────────────────────────────────────────────────────────────────────────────

def show_venv_instructions() -> None:
    """Display comprehensive virtualenv and pip usage guide with tips."""
    import sys as _sys
    hr("Virtual Environments & Package Management")

    print(textwrap.dedent("""\
    Why use virtual environments?
    ──────────────────────────────
    Virtual environments are isolated Python environments that allow you to:
    • Install packages without affecting your system Python
    • Use different package versions for different projects
    • Avoid dependency conflicts between projects
    • Make your project reproducible on other machines
    • Keep your global Python installation clean

    Creating a Virtual Environment
    ───────────────────────────────
    The 'venv' module is built into Python 3.3+ and is the recommended way:

        # Create virtual environment (run once per project)
        python -m venv .venv

    The '.venv' folder will contain your isolated Python installation.

    Activating the Virtual Environment
    ───────────────────────────────────
    You must activate before using it:

        macOS / Linux:
            source .venv/bin/activate

        Windows Command Prompt:
            .venv\\Scripts\\activate.bat

        Windows PowerShell:
            .venv\\Scripts\\Activate.ps1

    Your terminal prompt will change to show (.venv) when active.

    Installing Packages
    ───────────────────
    Once activated, use pip to install packages:

        # Upgrade pip first (recommended)
        python -m pip install --upgrade pip

        # Install packages
        python -m pip install requests
        python -m pip install pandas numpy

        # Install from requirements.txt
        python -m pip install -r requirements.txt

    Note: Always use 'python -m pip' instead of just 'pip' to ensure
    you're installing into the correct environment.

    Managing Dependencies
    ─────────────────────
        # Save currently installed packages
        python -m pip freeze > requirements.txt

        # Later, recreate environment from requirements.txt
        python -m pip install -r requirements.txt

    Deactivating
    ────────────
    When you're done working:

        deactivate

    Common Troubleshooting
    ──────────────────────
    • "Command not found": Make sure Python is in your PATH
    • PowerShell execution policy (Windows):
        Run as Administrator:
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    • Wrong Python name: Use 'python3' instead of 'python' on some systems

    Best Practices
    ──────────────
    • Create one virtual environment per project
    • Add .venv to your .gitignore (don't commit it)
    • Activate the environment every time you work on the project
    • Keep requirements.txt updated
    • Use descriptive names: 'myproject_env' instead of just 'venv'

    Learn More
    ──────────
    • venv (official docs): https://docs.python.org/3/library/venv.html
    • pip user guide: https://pip.pypa.io/en/stable/user_guide/
    • Packages tutorial: https://docs.python.org/3/tutorial/modules.html#packages
    • File I/O tutorial: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
    • doctest: https://docs.python.org/3/library/doctest.html
    """))

    # Show current environment status
    print("\n" + "=" * 60)
    print("Current Environment Status")
    print("=" * 60)

    in_venv = (hasattr(_sys, 'real_prefix') or
               (hasattr(_sys, 'base_prefix') and _sys.base_prefix != _sys.prefix))

    if in_venv:
        print("✓ You ARE currently in a virtual environment")
        print(f"  Python executable: {_sys.executable}")
        print(f"  Environment prefix: {_sys.prefix}")
    else:
        print("⚠ You are NOT in a virtual environment")
        print("  Consider creating and activating one for this project")

    print(f"\nPython version: {_sys.version}")
    print(f"pip version: (run 'python -m pip --version' to check)")


# ───────────────────────────────────────────────────────────────────────────────
# Task: Interactive demos split into smaller focused functions
# ───────────────────────────────────────────────────────────────────────────────

def demo_math_operations(base_dir: Path) -> None:
    """Demonstrate math_operations module (with retry loops and friendly messages)."""
    add_sys_path_once(base_dir)
    mo = import_fresh("math_operations")

    hr("Math Operations Demo")
    print("This module provides basic arithmetic: add, subtract, multiply, divide.")

    while True:
        first = input("\nEnter first number (or 'back' to return): ").strip()
        if first.lower() == "back":
            return
        try:
            a = float(first)
        except ValueError:
            print("Please enter a valid number.")
            continue

        second = input("Enter second number: ").strip()
        try:
            b = float(second)
        except ValueError:
            print("Please enter a valid number.")
            continue

        # Show all operations with formatted output
        print(f"\n{'Operation':<15} {'Expression':<22} {'Result':<15}")
        print("-" * 54)
        print(f"{'Addition':<15} {a} + {b:<15} = {mo.add(a, b)}")
        print(f"{'Subtraction':<15} {a} - {b:<15} = {mo.subtract(a, b)}")
        print(f"{'Multiplication':<15} {a} × {b:<15} = {mo.multiply(a, b)}")

        try:
            result = mo.divide(a, b)
            print(f"{'Division':<15} {a} ÷ {b:<15} = {result}")
        except ZeroDivisionError:
            print(f"{'Division':<15} {a} ÷ {b:<15} = ❌ Cannot divide by zero")

        again = input("\nTry with different numbers? (y/n): ").strip().lower()
        if again != 'y':
            break


def demo_string_operations(base_dir: Path) -> None:
    """Demonstrate string_utils module."""
    add_sys_path_once(base_dir)
    su = import_fresh("string_utils")

    hr("String Utilities Demo")
    print("This module provides string manipulation functions.")

    while True:
        s = input("\nEnter a string (or 'back' to return): ").strip()
        if s.lower() == 'back':
            return

        if not s:
            print("Please enter a non-empty string.")
            continue

        print(f"\nOriginal string:  '{s}'")
        print(f"Reversed:         '{su.reverse_string(s)}'")
        print(f"Vowel count:      {su.count_vowels(s)}")
        print(f"Length:           {len(s)} characters")

        again = input("\nTry another string? (y/n): ").strip().lower()
        if again != 'y':
            break


def demo_geometry(base_dir: Path) -> None:
    """Demonstrate geometry.circle package."""
    add_sys_path_once(base_dir)
    gc = import_fresh("geometry.circle")

    hr("Geometry / Circle Demo")
    print("This package provides circle calculations: area and circumference.")

    while True:
        s = input("\nEnter circle radius (or 'back' to return): ").strip()
        if s.lower() == "back":
            return
        try:
            r = float(s)
        except ValueError:
            print("Please enter a valid number.")
            continue

        try:
            area = gc.calculate_area(r)
            circ = gc.calculate_circumference(r)
            print(f"\nFor a circle with radius {r}:")
            print(f"  Area (πr²):           {area:.4f}")
            print(f"  Circumference (2πr):  {circ:.4f}")
            print(f"  Diameter (2r):        {2 * r:.4f}")
        except ValueError as e:
            print(f"❌ Error: {e} (radius must be non-negative)")
            continue

        again = input("\nCalculate for another radius? (y/n): ").strip().lower()
        if again != 'y':
            break


def demo_file_operations(base_dir: Path) -> None:
    """Demonstrate file_operations package (write/read a demo file)."""
    add_sys_path_once(base_dir)
    fr = import_fresh("file_operations.file_reader")
    fw = import_fresh("file_operations.file_writer")

    hr("File Operations Demo")
    print("This package provides simple file reading and writing.")
    demo_file = base_dir / "demo.txt"

    while True:
        print("\n1) Write to file")
        print("2) Read from file")
        print("0) Back to previous menu")

        choice = input("Choose: ").strip()

        if choice == "1":
            text = input("Enter text to write to demo.txt: ")
            try:
                n = fw.write_file(demo_file, text)
                print(f"✓ Successfully wrote {n} characters to {demo_file.name}")
            except Exception as e:
                print(f"❌ Error writing file: {e}")

        elif choice == "2":
            try:
                content = fr.read_file(demo_file)
                print(f"\nContent of {demo_file.name}:")
                print("-" * 40)
                print(content, end="" if content.endswith("\n") else "\n")
                print("-" * 40)
            except FileNotFoundError:
                print(f"❌ File {demo_file.name} does not exist yet.")
                print("Hint: Use option 1 to create it first.")
            except Exception as e:
                print(f"❌ Error reading file: {e}")

        elif choice == "0":
            return
        else:
            print("❌ Invalid option. Please choose 0, 1, or 2.")


def demo_usage(base_dir: Path) -> None:
    """Interactive menu that routes to individual demos."""
    while True:
        hr("Demo Menu")
        print("Choose which module/package to demonstrate:")
        print("1) Math Operations")
        print("2) String Utilities")
        print("3) Geometry (Circle)")
        print("4) File Operations")
        print("0) Back to main menu")

        choice = input("\nYour choice: ").strip()
        if choice == "1":
            demo_math_operations(base_dir)
        elif choice == "2":
            demo_string_operations(base_dir)
        elif choice == "3":
            demo_geometry(base_dir)
        elif choice == "4":
            demo_file_operations(base_dir)
        elif choice == "0":
            return
        else:
            print(f"❌ Invalid option '{choice}'. Please choose a number between 0 and 4.")
            print("Hint: Enter '0' to go back.")


# ───────────────────────────────────────────────────────────────────────────────
# Main CLI
# ───────────────────────────────────────────────────────────────────────────────

def main() -> None:
    hr("Lesson 11 — Modules, Packages, Doctests, venv")
    print("This script can generate modules/packages, run doctests, and show demos.\n")

    # Default project directory; can be changed if desired
    base_dir = Path.cwd() / "lesson11_project"

    while True:
        hr("Main Menu")
        print(f"Project directory: {base_dir}")
        print("1) Create/overwrite scaffold (modules/packages)")
        print("2) Run doctests for created modules")
        print("3) Demo usage (interactive)")
        print("4) Show virtualenv instructions")
        print("5) Change project directory")
        print("0) Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            res = create_scaffold(base_dir)
            print("\nScaffold created/updated. Files:")
            for p in res.created_files:
                print("  -", p.relative_to(base_dir.parent))
            print("\nTip: You can now run doctests (option 2) or demo (option 3).")

        elif choice == "2":
            if not base_dir.exists():
                print("⚠ Project directory does not exist. Create scaffold first (option 1).")
            else:
                run_created_doctests(base_dir)

        elif choice == "3":
            if not base_dir.exists():
                print("⚠ Project directory does not exist. Create scaffold first (option 1).")
            else:
                demo_usage(base_dir)

        elif choice == "4":
            show_venv_instructions()

        elif choice == "5":
            s = input("Enter new project directory path: ").strip()
            if not s:
                print("No change made.")
            else:
                base_dir = Path(s).expanduser().resolve()
                print(f"Project directory changed to: {base_dir}")

        elif choice == "0":
            print("Bye!")
            break

        else:
            print(f"❌ Invalid option '{choice}'. Please choose a number between 0 and 5.")
            print("Hint: Enter '0' to exit or '4' to see virtualenv instructions.")


if __name__ == "__main__":
    main()
