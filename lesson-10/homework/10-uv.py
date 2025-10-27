# lesson10.py
# ============================================================
# Three small apps in one file:
#   Task 1: ToDo List (with JSON persistence, "dirty" flag)
#   Task 2: Simple Blog System (edit/delete/latest, newest-first)
#   Task 3: Simple Banking System (Decimal money, safe transfer)
#
# All comments are in English (per assignment).
# The file provides:
#   - dataclasses with slots for memory efficiency
#   - strong validation and helpful error messages
#   - doctests to self-check key pieces
#   - simple CLI to demo features + run doctests
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Iterable, Tuple

# Money: set sane precision; operations quantized to cents by helper.
getcontext().prec = 28


# ------------------------ shared helpers ------------------------

def round_money(x: Decimal) -> Decimal:
    """Round a Decimal to two places (bank-style display), half-up.

    >>> round_money(Decimal('1'))
    Decimal('1.00')
    >>> round_money(Decimal('1.005'))
    Decimal('1.01')
    """
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_datetime(dt: datetime) -> str:
    """Human-friendly datetime format."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(d: Optional[date]) -> str:
    """Human-friendly date or dash if None."""
    return d.strftime("%Y-%m-%d") if d else "-"


def ask_int(prompt: str, *, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Robust integer reader with range validation and helpful prompts."""
    while True:
        s = input(prompt).strip()
        try:
            x = int(s)
            if min_val is not None and x < min_val:
                print(f"Value must be >= {min_val}.")
                continue
            if max_val is not None and x > max_val:
                print(f"Value must be <= {max_val}.")
                continue
            return x
        except ValueError:
            print("Please enter a valid integer.")


def ask_decimal(prompt: str, *, min_val: Optional[Decimal] = None) -> Decimal:
    """Robust Decimal reader with non-negative/positive validation."""
    while True:
        s = input(prompt).strip()
        try:
            amt = Decimal(s)
            if min_val is not None and amt < min_val:
                print(f"Amount must be >= {min_val}.")
                continue
            return amt
        except (InvalidOperation, ValueError):
            print("Please enter a valid number (e.g., 12.34).")


def ask_date(prompt: str) -> Optional[date]:
    """Read ISO date or blank for None."""
    while True:
        s = input(prompt + " (YYYY-MM-DD, empty to skip): ").strip()
        if not s:
            return None
        try:
            return date.fromisoformat(s)
        except ValueError:
            print("Please enter a valid ISO date (YYYY-MM-DD) or leave empty.")


# ============================================================
# Task 1 — ToDo List
# ============================================================

class TaskStatus(Enum):
    TODO = "TODO"
    DONE = "DONE"


@dataclass(slots=True)
class Task:
    """Single task with safe validation.

    >>> t = Task(id=1, title="Buy milk")
    >>> t.status is TaskStatus.TODO
    True
    """
    id: int
    title: str
    description: str = ""
    due_date: Optional[date] = None
    status: TaskStatus = TaskStatus.TODO

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title must be non-empty.")
        # Normalize whitespace in title
        self.title = self.title.strip()


@dataclass(slots=True)
class ToDoList:
    """In-memory tasks with JSON persistence and 'dirty' tracking."""
    _tasks: Dict[int, Task] = field(default_factory=dict)
    _next_id: int = 1
    _modified: bool = False

    # ---------- CRUD ----------
    def add_task(self, title: str, description: str = "", due_date: Optional[date] = None) -> Task:
        task = Task(id=self._next_id, title=title, description=description, due_date=due_date)
        self._tasks[task.id] = task
        self._next_id += 1
        self._modified = True
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def mark_complete(self, task_id: int) -> Tuple[bool, str]:
        """Mark a task as DONE by id. Returns (success, message).

        Distinguishes between "not found" and "already done".

        >>> td = ToDoList()
        >>> t = td.add_task("X")
        >>> td.mark_complete(9999)
        (False, 'Task not found')
        >>> td.mark_complete(t.id)
        (True, 'Task marked as complete')
        >>> td.mark_complete(t.id)
        (False, 'Task already completed')
        """
        task = self._tasks.get(task_id)
        if not task:
            return False, "Task not found"
        if task.status is TaskStatus.DONE:
            return False, "Task already completed"
        task.status = TaskStatus.DONE
        self._modified = True
        return True, "Task marked as complete"

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by id; returns True if removed."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._modified = True
            return True
        return False

    def list_all(self) -> List[Task]:
        """All tasks (stable by id)."""
        return [self._tasks[k] for k in sorted(self._tasks)]

    def list_incomplete(self) -> List[Task]:
        """Only TODO tasks."""
        return [t for t in self.list_all() if t.status is TaskStatus.TODO]

    # ---------- persistence ----------
    def save_to_file(self, filepath: Path) -> None:
        """Save tasks to JSON file (pretty-readable)."""
        import json
        data = {
            "next_id": self._next_id,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "due_date": t.due_date.isoformat() if t.due_date else None,
                    "status": t.status.value,
                }
                for t in self._tasks.values()
            ],
        }
        filepath.write_text(json.dumps(data, indent=2))
        self._modified = False

    @classmethod
    def load_from_file(cls, filepath: Path) -> "ToDoList":
        """Factory: load tasks from JSON if file exists; else empty list."""
        import json
        if not filepath.exists():
            return cls()
        data = json.loads(filepath.read_text())
        todo = cls()
        todo._next_id = int(data.get("next_id", 1))
        for td in data.get("tasks", []):
            task = Task(
                id=int(td["id"]),
                title=str(td["title"]),
                description=str(td.get("description", "")),
                due_date=date.fromisoformat(td["due_date"]) if td.get("due_date") else None,
                status=TaskStatus(str(td.get("status", "TODO"))),
            )
            todo._tasks[task.id] = task
        todo._modified = False
        return todo


# ------------------------ ToDo CLI ------------------------

def todo_cli() -> None:
    """Interactive demo for ToDoList with persistence and confirmations."""
    print("\n=== ToDo List ===")
    path = Path("todo_data.json")
    todo = ToDoList.load_from_file(path)
    print(f"Loaded {len(todo._tasks)} task(s) from {path!s}.\n")

    while True:
        print("[1] Add  [2] Complete  [3] Delete  [4] List all  [5] List incomplete  [6] Save  [0] Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            # Add with retry/cancel
            while True:
                title = input("Title (or 'cancel'): ").strip()
                if title.lower() == "cancel":
                    print("Cancelled.")
                    break
                desc = input("Description (optional): ").strip()
                due = ask_date("Due date")
                try:
                    t = todo.add_task(title, desc, due)
                    print(f"Added task #{t.id}: [{t.status.value}] {t.title} (due {format_date(t.due_date)})")
                    break
                except ValueError as e:
                    print(f"Error: {e}")
                    if input("Try again? (y/n): ").strip().lower() != "y":
                        break

        elif choice == "2":
            tid = ask_int("Task id to complete: ", min_val=1)
            ok, msg = todo.mark_complete(tid)
            print(msg)

        elif choice == "3":
            tid = ask_int("Task id to delete: ", min_val=1)
            task = todo.get_task(tid)
            if not task:
                print("Task not found.")
            else:
                print(f"Delete: [{task.status.value}] {task.title} (due {format_date(task.due_date)})")
                if input("Confirm (yes): ").strip().lower() == "yes":
                    todo.delete_task(tid)
                    print("Deleted.")
                else:
                    print("Cancelled.")

        elif choice == "4":
            tasks = todo.list_all()
            if not tasks:
                print("(empty)")
            else:
                for t in tasks:
                    print(f"#{t.id:03d} [{t.status.value}] {t.title}  due={format_date(t.due_date)}")
        elif choice == "5":
            tasks = todo.list_incomplete()
            if not tasks:
                print("(empty)")
            else:
                for t in tasks:
                    print(f"#{t.id:03d} [TODO] {t.title}  due={format_date(t.due_date)}")
        elif choice == "6":
            todo.save_to_file(path)
            print(f"Saved to {path}.")
        elif choice == "0":
            if todo._modified:
                save = input("You have unsaved changes. Save before exit? (y/n): ").strip().lower()
                if save == "y":
                    todo.save_to_file(path)
                    print(f"Saved to {path}.")
            break
        else:
            print("Unknown option.")
        print()


# ============================================================
# Task 2 — Simple Blog System
# ============================================================

@dataclass(slots=True)
class Post:
    """Blog post with timestamps.

    - Title is required and cannot be blank.
    - Content may be empty.
    - created_at is set per-instance via default_factory.
    """
    id: int
    title: str
    content: str
    author: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Title must be non-empty.")
        self.title = self.title.strip()

    def edit(self, *, title: Optional[str] = None, content: Optional[str] = None) -> None:
        """Edit title/content; updates timestamp.

        Note: title cannot be set to an empty/blank string.
        """
        if title is not None:
            if not title.strip():
                raise ValueError("Title must be non-empty.")
            self.title = title.strip()
        if content is not None:
            self.content = content
        self.updated_at = datetime.utcnow()

    @property
    def preview(self) -> str:
        """Short preview (60 chars)."""
        text = self.content.replace("\n", " ")
        return text if len(text) <= 60 else text[:57] + "..."


@dataclass(slots=True)
class Blog:
    """Blog: manage posts with newest-first listings by default."""
    _posts: Dict[int, Post] = field(default_factory=dict)
    _next_id: int = 1

    def add_post(self, title: str, content: str, author: str) -> Post:
        p = Post(id=self._next_id, title=title, content=content, author=author)
        self._posts[p.id] = p
        self._next_id += 1
        return p

    def get(self, post_id: int) -> Optional[Post]:
        return self._posts.get(post_id)

    def delete_post(self, post_id: int) -> bool:
        if post_id in self._posts:
            del self._posts[post_id]
            return True
        return False

    def list_all(self, *, newest_first: bool = True) -> List[Post]:
        posts = list(self._posts.values())
        posts.sort(key=lambda p: p.created_at, reverse=newest_first)
        return posts

    def by_author(self, author: str, *, newest_first: bool = True) -> List[Post]:
        posts = [p for p in self._posts.values() if p.author == author]
        posts.sort(key=lambda p: p.created_at, reverse=newest_first)
        return posts

    def latest(self, n: int = 5) -> List[Post]:
        """Return up to n latest posts (fewer if total < n)."""
        return self.list_all(newest_first=True)[:n]


# ------------------------ Blog CLI ------------------------

def blog_cli() -> None:
    """Interactive demo for Blog."""
    print("\n=== Blog ===")
    blog = Blog()
    while True:
        print("[1] Add  [2] List all  [3] By author  [4] Edit  [5] Delete  [6] Latest  [0] Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            while True:
                title = input("Title (or 'cancel'): ").strip()
                if title.lower() == "cancel":
                    print("Cancelled.")
                    break
                author = input("Author: ").strip()
                content = input("Content: ").strip()
                try:
                    p = blog.add_post(title, content, author)
                    print(f"Added post #{p.id} at {format_datetime(p.created_at)}Z")
                    break
                except ValueError as e:
                    print(f"Error: {e}")
                    if input("Try again? (y/n): ").strip().lower() != "y":
                        break

        elif ch == "2":
            posts = blog.list_all()
            if not posts:
                print("(empty)")
            for p in posts:
                print(f"#{p.id:03d} [{format_datetime(p.created_at)}Z] {p.title} — {p.author} | {p.preview}")

        elif ch == "3":
            a = input("Author: ").strip()
            posts = blog.by_author(a)
            if not posts:
                print("(empty)")
            for p in posts:
                print(f"#{p.id:03d} [{format_datetime(p.created_at)}Z] {p.title} — {p.author} | {p.preview}")

        elif ch == "4":
            pid = ask_int("Post id to edit: ", min_val=1)
            p = blog.get(pid)
            if not p:
                print("Post not found.")
            else:
                new_title = input("New title (blank=keep): ")
                new_content = input("New content (blank=keep): ")
                kwargs = {}
                if new_title.strip():
                    kwargs["title"] = new_title
                if new_content != "":
                    kwargs["content"] = new_content
                try:
                    if kwargs:
                        p.edit(**kwargs)
                        print("Updated.")
                    else:
                        print("No changes.")
                except ValueError as e:
                    print(f"Error: {e}")

        elif ch == "5":
            pid = ask_int("Post id to delete: ", min_val=1)
            p = blog.get(pid)
            if not p:
                print("Post not found.")
            else:
                print(f"You are about to delete: [{p.title}] by {p.author}")
                if input("Are you sure? (yes/no): ").strip().lower() == "yes":
                    print("Deleted." if blog.delete_post(pid) else "Post not found.")
                else:
                    print("Cancelled.")

        elif ch == "6":
            n = ask_int("How many latest posts?: ", min_val=1, max_val=50)
            for p in blog.latest(n):
                print(f"#{p.id:03d} [{format_datetime(p.created_at)}Z] {p.title} — {p.author}")

        elif ch == "0":
            break
        else:
            print("Unknown option.")
        print()


# ============================================================
# Task 3 — Simple Banking System
# ============================================================

class BankError(Exception):
    """Base class for banking-related exceptions."""


class DuplicateAccountError(BankError):
    pass


class AccountNotFoundError(BankError):
    pass


class InsufficientFundsError(BankError):
    pass


@dataclass(slots=True)
class Account:
    """Simple bank account with optional overdraft (stored as Decimal cents)."""
    number: int
    holder: str
    balance: Decimal = field(default_factory=lambda: Decimal("0"))
    overdraft_limit: Decimal = field(default_factory=lambda: Decimal("0"))

    def deposit(self, amount: Decimal) -> None:
        """Deposit positive amount into account.

        >>> a = Account(1, "Alice")
        >>> a.deposit(Decimal('10'))
        >>> str(a.balance)
        '10'
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance = self.balance + amount

    def withdraw(self, amount: Decimal) -> None:
        """Withdraw if within balance+overdraft; round to cents after op."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        new_balance = self.balance - amount
        # Allow negative balance down to -overdraft_limit
        if new_balance < -self.overdraft_limit:
            raise InsufficientFundsError("Insufficient funds considering overdraft.")
        self.balance = new_balance

    @property
    def pretty_balance(self) -> str:
        return f"{round_money(self.balance):.2f}"


@dataclass(slots=True)
class Bank:
    """Bank storing accounts in a dict and providing safe transfer with rollback."""
    _accounts: Dict[int, Account] = field(default_factory=dict)

    # ---------- account ops ----------
    def add_account(self, number: int, holder: str, balance: Decimal = Decimal("0"),
                    overdraft_limit: Decimal = Decimal("0")) -> Account:
        if number in self._accounts:
            raise DuplicateAccountError(f"Account {number} already exists.")
        acc = Account(number, holder, balance, overdraft_limit)
        self._accounts[number] = acc
        return acc

    def get(self, number: int) -> Account:
        acc = self._accounts.get(number)
        if not acc:
            raise AccountNotFoundError(f"Account {number} not found.")
        return acc

    def deposit(self, number: int, amount: Decimal) -> None:
        self.get(number).deposit(amount)

    def withdraw(self, number: int, amount: Decimal) -> None:
        self.get(number).withdraw(amount)

    # ---------- transfer with explicit rollback ----------
    def transfer(self, from_id: int, to_id: int, amount: Decimal) -> None:
        """Transfer with rollback on failure.

        Raises
        ------
        ValueError
            If amount <= 0
        AccountNotFoundError
            If either account doesn't exist
        InsufficientFundsError
            If source has insufficient funds (incl. overdraft)
        RuntimeError
            If deposit fails after withdrawal; we restore source balance directly

        >>> bank = Bank()
        >>> bank.add_account(1, "A", Decimal('100'))
        Account(number=1, holder='A', balance=Decimal('100'), overdraft_limit=Decimal('0'))
        >>> bank.add_account(2, "B", Decimal('0'))
        Account(number=2, holder='B', balance=Decimal('0'), overdraft_limit=Decimal('0'))
        >>> bank.transfer(1, 2, Decimal('40'))
        >>> (bank.get(1).balance, bank.get(2).balance)
        (Decimal('60'), Decimal('40'))
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")

        # Validate existence BEFORE mutation
        src = self.get(from_id)
        dst = self.get(to_id)

        # Withdraw first (this validates sufficient funds)
        original_src_balance = src.balance
        src.withdraw(amount)

        try:
            # Try deposit
            dst.deposit(amount)
        except Exception as deposit_error:
            # Rollback: restore original source balance directly
            try:
                src.balance = original_src_balance
            except Exception as rollback_error:
                raise RuntimeError(
                    f"CRITICAL: Transfer failed and rollback failed. "
                    f"Source account {from_id} may be inconsistent. "
                    f"Deposit error: {deposit_error}; rollback error: {rollback_error}"
                ) from deposit_error
            # Rollback succeeded
            raise RuntimeError(f"Transfer failed, rolled back: {deposit_error}") from deposit_error


# ------------------------ Bank CLI ------------------------

def bank_cli() -> None:
    """Interactive demo for Bank with Decimal money ops."""
    print("\n=== Bank ===")
    bank = Bank()
    while True:
        print("[1] Add  [2] Balance  [3] Deposit  [4] Withdraw  [5] Transfer  [6] Accounts  [0] Back")
        ch = input("Choose: ").strip()
        try:
            if ch == "1":
                number = ask_int("Account number: ", min_val=1)
                holder = input("Holder: ").strip() or "Unnamed"
                bal = ask_decimal("Initial balance (>=0): ", min_val=Decimal("0"))
                od = ask_decimal("Overdraft limit (>=0): ", min_val=Decimal("0"))
                acc = bank.add_account(number, holder, bal, od)
                print(f"Created account #{acc.number} ({acc.holder}), balance={acc.pretty_balance}, OD={round_money(acc.overdraft_limit):.2f}")

            elif ch == "2":
                number = ask_int("Account number: ", min_val=1)
                acc = bank.get(number)
                print(f"Account #{acc.number} — holder={acc.holder}, balance={acc.pretty_balance}, OD={round_money(acc.overdraft_limit):.2f}")

            elif ch == "3":
                number = ask_int("Account number: ", min_val=1)
                amt = ask_decimal("Amount to deposit (>0): ", min_val=Decimal("0.01"))
                bank.deposit(number, amt)
                print("Deposited.")

            elif ch == "4":
                number = ask_int("Account number: ", min_val=1)
                amt = ask_decimal("Amount to withdraw (>0): ", min_val=Decimal("0.01"))
                bank.withdraw(number, amt)
                print("Withdrawn.")

            elif ch == "5":
                src = ask_int("From: ", min_val=1)
                dst = ask_int("To: ", min_val=1)
                amt = ask_decimal("Amount (>0): ", min_val=Decimal("0.01"))
                bank.transfer(src, dst, amt)
                print("Transferred.")

            elif ch == "6":
                if not bank._accounts:
                    print("(empty)")
                else:
                    for acc in bank._accounts.values():
                        print(f"#{acc.number}  holder={acc.holder}  bal={acc.pretty_balance}  OD={round_money(acc.overdraft_limit):.2f}")

            elif ch == "0":
                break
            else:
                print("Unknown option.")
        except BankError as be:
            print(f"[Bank error] {be}")
        except ValueError as ve:
            print(f"[Input error] {ve}")
        print()


# ============================================================
# Main menu + doctest runner
# ============================================================

def run_doctests(verbose: bool = False) -> None:
    import doctest, sys
    fails, _ = doctest.testmod(verbose=verbose)
    if fails == 0:
        print("All doctests passed.")
    else:
        print(f"{fails} doctest(s) failed.")
        sys.exit(1)


def main() -> None:
    while True:
        print("\n=== Main Menu ===")
        print("[1] ToDo List  [2] Blog  [3] Bank  [9] Run doctests  [0] Exit")
        ch = input("Choose: ").strip()
        if ch == "1":
            todo_cli()
        elif ch == "2":
            blog_cli()
        elif ch == "3":
            bank_cli()
        elif ch == "9":
            run_doctests(verbose=True)
        elif ch == "0":
            print("Bye!")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    # Quiet doctest run on script start, then show menu.
    run_doctests(verbose=False)
    main()
