from __future__ import annotations
from typing import List, Tuple, Sequence, TypeVar, Optional

T = TypeVar("T")

# Task 1: third fruit
def third_fruit(fruits: Sequence[str]) -> str:
    """
    Return the 3rd item (index 2).

    >>> third_fruit(["apple", "banana", "orange", "kiwi", "mango"])
    'orange'
    """
    return fruits[2]

# Task 2: concatenate two lists
def concat_lists(a: List[T], b: List[T]) -> List[T]:
    """
    >>> concat_lists([1, 2, 3], [4, 5])
    [1, 2, 3, 4, 5]
    """
    return a + b

# Task 3: first, middle, last
def first_middle_last(items: Sequence[T]) -> List[T]:
    """
    Take first, middle (floor for even), and last.

    >>> first_middle_last([10, 20, 30, 40, 50])
    [10, 30, 50]
    >>> first_middle_last([1, 2, 3, 4])  # middle = index len//2 = 2
    [1, 3, 4]
    """
    n = len(items)
    mid = n // 2
    return [items[0], items[mid], items[-1]]

# Task 4: list -> tuple
def list_to_tuple(items: List[T]) -> Tuple[T, ...]:
    """
    >>> list_to_tuple(["Interstellar", "Inception"])  # doctest: +NORMALIZE_WHITESPACE
    ('Interstellar', 'Inception')
    """
    return tuple(items)

# Task 5: check Paris in list (case-sensitive)
def contains_paris(cities: Sequence[str]) -> bool:
    """
    >>> contains_paris(["Tashkent", "Paris", "Tokyo"])
    True
    >>> contains_paris(["paris"])
    False
    """
    return "Paris" in cities

# Task 6: duplicate list without loops
def duplicate_list(items: List[T]) -> List[T]:
    """
    >>> duplicate_list([1, 2, 3])
    [1, 2, 3, 1, 2, 3]
    """
    return items * 2

# Task 7: swap first and last (returns new list; safe for 0/1 length)
def swap_first_last(items: List[T]) -> List[T]:
    """
    >>> swap_first_last([10, 20, 30, 40])
    [40, 20, 30, 10]
    >>> swap_first_last([42])
    [42]
    >>> swap_first_last([])
    []
    """
    if len(items) < 2:
        return items.copy()
    out = items.copy()
    out[0], out[-1] = out[-1], out[0]
    return out

# Task 8: slice tuple (indexes 3..7 inclusive)
def slice_tuple_3_to_7(t: Tuple[int, ...]) -> Tuple[int, ...]:
    """
    >>> slice_tuple_3_to_7(tuple(range(1, 11)))
    (4, 5, 6, 7, 8)
    """
    return t[3:8]

# Task 9: count "blue"
def count_blue(colors: Sequence[str]) -> int:
    """
    >>> count_blue(["red", "blue", "green", "blue", "blue"])
    3
    """
    return list(colors).count("blue")

# Task 10: index of "lion" in tuple (None if not found)
def index_of_lion(animals: Tuple[str, ...]) -> Optional[int]:
    """
    >>> index_of_lion(("cat", "dog", "lion", "tiger"))
    2
    >>> index_of_lion(("cat", "dog")) is None
    True
    """
    try:
        return animals.index("lion")
    except ValueError:
        return None

# Task 11: merge two tuples
def merge_tuples(a: Tuple[T, ...], b: Tuple[T, ...]) -> Tuple[T, ...]:
    """
    >>> merge_tuples((1, 2, 3), (4, 5))
    (1, 2, 3, 4, 5)
    """
    return a + b

# Task 12: lengths of list and tuple
def lengths(lst: List[T], tup: Tuple[T, ...]) -> Tuple[int, int]:
    """
    >>> lengths([1, 2, 3, 4], (10, 20, 30))
    (4, 3)
    """
    return len(lst), len(tup)

# Task 13: tuple -> list
def tuple_to_list(t: Tuple[T, ...]) -> List[T]:
    """
    >>> tuple_to_list((2, 4, 6))
    [2, 4, 6]
    """
    return list(t)

# Task 14: max & min of tuple (non-empty)
def tuple_max_min(t: Tuple[int, ...]) -> Tuple[int, int]:
    """
    >>> tuple_max_min((3, 7, 2, 9, 5))
    (9, 2)
    """
    return max(t), min(t)

# Task 15: reverse tuple
def reverse_tuple(t: Tuple[T, ...]) -> Tuple[T, ...]:
    """
    >>> reverse_tuple(("alpha", "beta", "gamma"))
    ('gamma', 'beta', 'alpha')
    """
    return t[::-1]


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
