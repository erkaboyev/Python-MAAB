# lesson9.py — OOP exercises with doctests and a small CLI
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation, getcontext
from typing import Any, Optional, Generator, Iterable
from collections import deque
from abc import ABC, abstractmethod

# Configure Decimal precision for financial calculations
getcontext().prec = 28


# ===========================
# Helpers (CLI and utilities)
# ===========================

def read_int(prompt: str, *, min_val: int | None = None, max_val: int | None = None) -> int:
    """Read an integer with optional bounds; re-prompt until valid."""
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


def read_decimal(prompt: str, *, min_val: Decimal | None = None) -> Decimal:
    """Read a Decimal value; optional lower bound."""
    while True:
        s = input(prompt).strip()
        try:
            x = Decimal(s)
            if min_val is not None and x < min_val:
                print(f"Enter a number >= {min_val}")
                continue
            return x
        except (InvalidOperation, ValueError):
            print("Please enter a numeric value (e.g., 12.34).")


# ===========================
# Task 4 (base): Shape (ABC)
# ===========================

class Shape(ABC):
    """Abstract shape interface."""

    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...


# ===========================
# Task 1: Circle class
# ===========================

@dataclass
class Circle(Shape):
    """Circle with non-negative radius.

    >>> c = Circle(3.0)
    >>> round(c.area(), 4)
    28.2743
    >>> round(c.circumference(), 4)
    18.8496
    >>> round(c.perimeter(), 4)  # alias for circumference()
    18.8496
    >>> Circle(-1.0)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ValueError: ...
    """
    radius: float

    def __post_init__(self) -> None:
        if self.radius < 0:
            raise ValueError("Radius must be non-negative.")

    def area(self) -> float:
        """π r^2"""
        return math.pi * (self.radius ** 2)

    def circumference(self) -> float:
        """2πr"""
        return 2.0 * math.pi * self.radius

    # Keep perimeter() for compatibility; prefer circumference() for circles
    def perimeter(self) -> float:
        return self.circumference()


# ===========================
# Task 4: Other shapes
# ===========================

@dataclass
class Square(Shape):
    """Square with side >= 0.

    >>> s = Square(4)
    >>> s.area(), s.perimeter()
    (16, 16)
    """
    side: float

    def __post_init__(self) -> None:
        if self.side < 0:
            raise ValueError("Side must be non-negative.")

    def area(self) -> float:
        return self.side * self.side

    def perimeter(self) -> float:
        return 4 * self.side


@dataclass
class Triangle(Shape):
    """Triangle by three sides (Heron's formula).

    >>> t = Triangle(3, 4, 5)
    >>> round(t.area(), 5)
    6.0
    >>> t.perimeter()
    12
    >>> Triangle(1, 2, 10)  # invalid
    Traceback (most recent call last):
    ValueError: Invalid triangle sides.
    """
    a: float
    b: float
    c: float

    def __post_init__(self) -> None:
        a, b, c = self.a, self.b, self.c
        if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Invalid triangle sides.")

    def perimeter(self) -> float:
        return self.a + self.b + self.c

    def area(self) -> float:
        # Heron's formula; guard against tiny negative due to FP error
        s = self.perimeter() / 2.0
        return math.sqrt(max(s * (s - self.a) * (s - self.b) * (s - self.c), 0.0))


# ===========================
# Task 2: Person class
# ===========================

@dataclass
class Person:
    """Person with name, country and date of birth.

    Age calculation subtracts 1 if birthday hasn't occurred yet this year.

    >>> p = Person(name="Alice", country="UK", dob=date(2000, 6, 1))
    >>> isinstance(p.age_on(date(2024, 6, 1)), int)
    True
    >>> p.age_on(date(2024, 5, 31))
    23
    >>> p.age() >= 0  # on today
    True
    """
    name: str
    country: str
    dob: date

    def age_on(self, on_date: date) -> int:
        """Return age in full years on given date."""
        years = on_date.year - self.dob.year
        before_birthday = (on_date.month, on_date.day) < (self.dob.month, self.dob.day)
        return years - (1 if before_birthday else 0)

    def age(self) -> int:
        """Age as of today."""
        return self.age_on(date.today())


# ===========================
# Task 3: Calculator class
# ===========================

class Calculator:
    """Basic arithmetic operations (stateless)."""

    @staticmethod
    def add(a: float, b: float) -> float: return a + b

    @staticmethod
    def sub(a: float, b: float) -> float: return a - b

    @staticmethod
    def mul(a: float, b: float) -> float: return a * b

    @staticmethod
    def div(a: float, b: float) -> float:
        """Divide a by b; raises ZeroDivisionError if b == 0."""
        return a / b


# =================================================
# Task 5: Binary Search Tree (insert, search, inorder)
# =================================================

@dataclass
class BSTNode:
    key: int
    left: Optional['BSTNode'] = None
    right: Optional['BSTNode'] = None
    count: int = 1  # used only if on_duplicate="count"


class BinarySearchTree:
    """Binary Search Tree with insert/search.

    `on_duplicate` policy:
      - "ignore" (default): silently skip duplicates
      - "error": raise ValueError
      - "count": keep a frequency counter in nodes

    >>> bst = BinarySearchTree()
    >>> for k in [5, 3, 7, 1, 4, 6, 8]:
    ...     bst.insert(k)
    >>> bst.search(4)
    True
    >>> bst.search(10)
    False
    >>> list(bst.inorder())
    [1, 3, 4, 5, 6, 7, 8]
    >>> bst2 = BinarySearchTree(on_duplicate="count")
    >>> for k in [2, 2, 2, 1]:
    ...     bst2.insert(k)
    >>> list(bst2.inorder_with_counts())
    [(1, 1), (2, 3)]
    """

    def __init__(self, *, on_duplicate: str = "ignore") -> None:
        if on_duplicate not in {"ignore", "error", "count"}:
            raise ValueError("on_duplicate must be 'ignore', 'error', or 'count'")
        self.root: Optional[BSTNode] = None
        self.on_duplicate = on_duplicate

    def insert(self, key: int) -> None:
        if self.root is None:
            self.root = BSTNode(key)
            return
        cur = self.root
        while True:
            if key == cur.key:
                if self.on_duplicate == "ignore":
                    return
                elif self.on_duplicate == "error":
                    raise ValueError(f"Duplicate key: {key}")
                else:  # "count"
                    cur.count += 1
                    return
            elif key < cur.key:
                if cur.left is None:
                    cur.left = BSTNode(key)
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = BSTNode(key)
                    return
                cur = cur.right

    def search(self, key: int) -> bool:
        cur = self.root
        while cur:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def inorder(self) -> Generator[int, None, None]:
        """Inorder traversal (sorted keys)."""
        def _in(n: Optional[BSTNode]):
            if not n: return
            yield from _in(n.left)
            yield n.key
            yield from _in(n.right)
        yield from _in(self.root)

    def inorder_with_counts(self) -> Generator[tuple[int, int], None, None]:
        """Inorder traversal yielding (key, count)."""
        def _in(n: Optional[BSTNode]):
            if not n: return
            yield from _in(n.left)
            yield (n.key, n.count)
            yield from _in(n.right)
        yield from _in(self.root)


# =======================================
# Task 6 & 9: Stack (with display)
# =======================================

class Stack:
    """Simple LIFO stack based on Python list.

    >>> st = Stack()
    >>> st.is_empty()
    True
    >>> st.push(1); st.push(2); st.display()
    [1, 2]
    >>> bool(st)
    True
    >>> st.peek()
    2
    >>> st.pop()
    2
    >>> len(st)
    1
    """

    def __init__(self) -> None:
        self._data: list[Any] = []

    def push(self, x: Any) -> None:
        self._data.append(x)

    def pop(self) -> Any:
        if not self._data:
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self) -> bool:
        return not self._data

    def display(self) -> list[Any]:
        """Return a shallow copy for display."""
        return list(self._data)

    def clear(self) -> None:
        """Remove all elements from the stack."""
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        """Truthiness reflects non-emptiness."""
        return bool(self._data)


# =======================================
# Task 7: Singly Linked List
# =======================================

@dataclass
class LLNode:
    value: Any
    next: Optional['LLNode'] = None


class LinkedList:
    """Singly linked list with insert and delete operations.

    >>> ll = LinkedList()
    >>> ll.insert_tail(1); ll.insert_tail(2); ll.insert_head(0)
    >>> ll.to_list()
    [0, 1, 2]
    >>> list(iter(ll))
    [0, 1, 2]
    >>> len(ll)
    3
    >>> ll.delete_value(1)
    True
    >>> ll.to_list()
    [0, 2]
    >>> ll.delete_value(42)
    False
    """

    def __init__(self) -> None:
        self.head: Optional[LLNode] = None
        self.tail: Optional[LLNode] = None

    def insert_head(self, value: Any) -> None:
        node = LLNode(value, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node

    def insert_tail(self, value: Any) -> None:
        node = LLNode(value, None)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node

    def delete_value(self, value: Any) -> bool:
        """Delete first occurrence of value; return True if deleted."""
        prev: Optional[LLNode] = None
        cur = self.head
        while cur:
            if cur.value == value:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                if cur is self.tail:
                    self.tail = prev
                return True
            prev, cur = cur, cur.next
        return False

    def to_list(self) -> list[Any]:
        return list(iter(self))

    def __iter__(self) -> Generator[Any, None, None]:
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def __len__(self) -> int:
        return sum(1 for _ in self)


# =======================================
# Task 8: Shopping Cart (Decimal money)
# =======================================

@dataclass
class CartItem:
    name: str
    unit_price: Decimal
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if self.unit_price < 0:
            raise ValueError("Unit price must be non-negative.")

    def __repr__(self) -> str:
        return f"CartItem(name={self.name!r}, unit_price={self.unit_price}, quantity={self.quantity})"


class ShoppingCart:
    """Shopping cart with precise Decimal money arithmetic.

    Behavior with repeated items:
    - If strict_price=True, adding the same item with different price raises ValueError.
    - Quantity is accumulated.

    >>> cart = ShoppingCart()
    >>> cart.add_item("Book", Decimal("12.49"), 2)
    >>> cart.add_item("Pen", Decimal("1.20"), 3)
    >>> cart.total()
    Decimal('28.58')
    >>> cart.remove_item("Pen")
    True
    >>> cart.total()
    Decimal('24.98')
    """

    def __init__(self, *, strict_price: bool = True) -> None:
        self._items: dict[str, CartItem] = {}
        self._strict_price = strict_price

    def add_item(self, name: str, unit_price: Decimal, quantity: int = 1) -> None:
        if name in self._items:
            item = self._items[name]
            if self._strict_price and item.unit_price != unit_price:
                raise ValueError(
                    f"Price mismatch for {name}: existing {item.unit_price}, new {unit_price}"
                )
            new_qty = item.quantity + quantity
            if new_qty <= 0:
                raise ValueError("Resulting quantity must be positive.")
            # keep original price (documented behavior)
            self._items[name] = CartItem(name, item.unit_price, new_qty)
        else:
            self._items[name] = CartItem(name, unit_price, quantity)

    def remove_item(self, name: str) -> bool:
        return self._items.pop(name, None) is not None

    def items(self) -> list[CartItem]:
        return list(self._items.values())

    def total(self) -> Decimal:
        total = sum((it.unit_price * it.quantity for it in self._items.values()), Decimal("0"))
        # Financial rounding to 2 decimals
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# =======================================
# Task 10: Queue (FIFO)
# =======================================

class Queue:
    """Queue based on collections.deque for O(1) appends/pops at both ends.

    >>> q = Queue()
    >>> q.is_empty()
    True
    >>> q.enqueue(1); q.enqueue(2); q.dequeue()
    1
    >>> q.peek()
    2
    """

    def __init__(self) -> None:
        self._dq: deque[Any] = deque()

    def enqueue(self, x: Any) -> None:
        self._dq.append(x)

    def dequeue(self) -> Any:
        if not self._dq:
            raise IndexError("dequeue from empty queue")
        return self._dq.popleft()

    def peek(self) -> Any:
        if not self._dq:
            raise IndexError("peek from empty queue")
        return self._dq[0]

    def is_empty(self) -> bool:
        return not self._dq

    def __len__(self) -> int:
        return len(self._dq)


# =======================================
# Task 11: Bank and Accounts
# =======================================

class InsufficientFundsError(RuntimeError): ...
class AccountNotFoundError(KeyError): ...
class DuplicateAccountError(KeyError): ...


@dataclass
class Account:
    account_id: int
    owner: str
    balance: Decimal = field(default_factory=lambda: Decimal("0"))

    def deposit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient funds.")
        self.balance -= amount

    def __repr__(self) -> str:
        return f"Account(id={self.account_id}, owner={self.owner!r}, balance={self.balance})"

    @property
    def balance_view(self) -> Decimal:
        """Read-only alias for external APIs."""
        return self.balance


class Bank:
    """Bank managing multiple accounts and transfers.

    >>> bank = Bank()
    >>> bank.create_account(1, "Alice", Decimal("100"))
    >>> bank.create_account(2, "Bob", Decimal("50"))
    >>> bank.transfer(1, 2, Decimal("20"))
    >>> bank.get_balance(1), bank.get_balance(2)
    (Decimal('80'), Decimal('70'))
    >>> bank.withdraw(2, Decimal("1000"))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    InsufficientFundsError: ...
    """

    def __init__(self) -> None:
        self._accounts: dict[int, Account] = {}

    def create_account(self, account_id: int, owner: str, initial: Decimal = Decimal("0")) -> None:
        if account_id in self._accounts:
            raise DuplicateAccountError(f"Account {account_id} already exists.")
        if initial < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._accounts[account_id] = Account(account_id, owner, initial)

    def get_account(self, account_id: int) -> Account:
        acc = self._accounts.get(account_id)
        if acc is None:
            raise AccountNotFoundError(f"Account {account_id} not found.")
        return acc

    def deposit(self, account_id: int, amount: Decimal) -> None:
        self.get_account(account_id).deposit(amount)

    def withdraw(self, account_id: int, amount: Decimal) -> None:
        self.get_account(account_id).withdraw(amount)

    def transfer(self, from_id: int, to_id: int, amount: Decimal) -> None:
        """Transfer with rollback on deposit failure."""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        src = self.get_account(from_id)
        dst = self.get_account(to_id)

        # Withdraw first (validates sufficient funds)
        src.withdraw(amount)

        try:
            # Attempt deposit to destination
            dst.deposit(amount)
        except Exception as e:
            # Rollback: restore withdrawn amount for consistency
            src.deposit(amount)
            raise RuntimeError(f"Transfer failed, rolled back: {e}") from e

    def get_balance(self, account_id: int) -> Decimal:
        return self.get_account(account_id).balance


# =======================
# Minimal CLI for demo
# =======================

def _menu() -> None:
    print("=== Lesson 9: OOP Exercises ===")
    print("0) Exit")
    print("1) Circle area/perimeter")
    print("2) Person age")
    print("3) Calculator")
    print("4) Shapes: Square, Triangle")
    print("5) Binary Search Tree")
    print("6) Stack demo")
    print("7) LinkedList demo")
    print("8) ShoppingCart demo")
    print("9) Queue demo")
    print("10) Bank demo")

    while True:
        choice = read_int("Choose: ", min_val=0, max_val=10)
        if choice == 0:
            print("Bye!")
            return

        try:
            if choice == 1:
                r = float(input("Radius: "))
                c = Circle(r)
                print("Area:", c.area())
                print("Circumference:", c.circumference())

            elif choice == 2:
                name = input("Name: ").strip() or "John"
                country = input("Country: ").strip() or "UZ"
                y = read_int("Birth year: ", min_val=1)
                m = read_int("Birth month: ", min_val=1, max_val=12)
                d = read_int("Birth day: ", min_val=1, max_val=31)
                p = Person(name, country, date(y, m, d))
                print("Age today:", p.age())

            elif choice == 3:
                a = float(input("a: ")); b = float(input("b: "))
                print("add:", Calculator.add(a, b))
                print("sub:", Calculator.sub(a, b))
                print("mul:", Calculator.mul(a, b))
                try:
                    print("div:", Calculator.div(a, b))
                except ZeroDivisionError as e:
                    print("Error:", e)

            elif choice == 4:
                s = Square(float(input("Square side: ")))
                print("Square area:", s.area(), "perimeter:", s.perimeter())
                a = float(input("Triangle a: "))
                b = float(input("Triangle b: "))
                c = float(input("Triangle c: "))
                t = Triangle(a, b, c)
                print("Triangle area:", t.area(), "perimeter:", t.perimeter())

            elif choice == 5:
                policy = input("on_duplicate [ignore|error|count] (default ignore): ").strip() or "ignore"
                bst = BinarySearchTree(on_duplicate=policy)
                raw = input("Enter integers (space-separated): ").strip()
                for token in raw.split():
                    bst.insert(int(token))
                if policy == "count":
                    print("Inorder (key,count):", list(bst.inorder_with_counts()))
                else:
                    print("Inorder keys:", list(bst.inorder()))
                k = read_int("Search key: ")
                print("Found?", bst.search(k))

            elif choice == 6:
                st = Stack()
                st.push("A"); st.push("B"); st.push("C")
                print("Stack:", st.display())
                print("Peek:", st.peek())
                print("Pop:", st.pop())
                print("Stack after pop:", st.display())
                st.clear()
                print("Cleared. Empty?", st.is_empty())

            elif choice == 7:
                ll = LinkedList()
                for v in [1, 2, 3]:
                    ll.insert_tail(v)
                ll.insert_head(0)
                print("LinkedList:", ll.to_list())
                print("Delete 2:", ll.delete_value(2), "->", ll.to_list())
                print("Iter:", list(iter(ll)), "len:", len(ll))

            elif choice == 8:
                cart = ShoppingCart(strict_price=True)
                cart.add_item("Laptop", Decimal("999.90"), 1)
                cart.add_item("Mouse", Decimal("20.00"), 2)
                print("Items:", cart.items())
                print("Total:", cart.total())
                cart.remove_item("Mouse")
                print("Total after removing Mouse:", cart.total())

            elif choice == 9:
                q = Queue()
                for v in [10, 20, 30]:
                    q.enqueue(v)
                print("Dequeue:", q.dequeue())
                print("Peek:", q.peek())
                print("Length:", len(q))

            elif choice == 10:
                bank = Bank()
                bank.create_account(1, "Alice", Decimal("100.00"))
                bank.create_account(2, "Bob", Decimal("50.00"))
                bank.transfer(1, 2, Decimal("25.00"))
                print("Balances:", bank.get_balance(1), bank.get_balance(2))
                try:
                    bank.withdraw(2, Decimal("1000"))
                except InsufficientFundsError as e:
                    print("Withdraw error:", e)

        except Exception as e:
            # Centralized user-facing error message (library code raises, CLI handles)
            print("Error:", e)

        print("-" * 40)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    _menu()
