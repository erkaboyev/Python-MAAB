# lesson4.py
from __future__ import annotations
from typing import Dict, List, Tuple, Iterable, Any, Sequence

# ===========================
# Dictionary Exercises
# ===========================

# Task 1: Sort the dictionary by value (↑ and ↓)
def task1_sort_by_value(d: Dict[Any, Any]) -> Tuple[Dict[Any, Any], Dict[Any, Any]]:
    """
    Return (ascending_dict, descending_dict) sorted by values.

    >>> task1_sort_by_value({"alice": 3, "bob": 1, "carol": 2})
    ({'bob': 1, 'carol': 2, 'alice': 3}, {'alice': 3, 'carol': 2, 'bob': 1})
    """
    asc_items = sorted(d.items(), key=lambda kv: kv[1])               # key= по значению
    desc_items = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
    return dict(asc_items), dict(desc_items)
# Reference on sorting with key=/reverse=: docs.python.org “Sorting HOWTO”. :contentReference[oaicite:0]{index=0}


# Task 2: Add a key to a dictionary
def task2_add_key(d: Dict[Any, Any], key: Any, value: Any) -> Dict[Any, Any]:
    """
    Return a NEW dict with (key, value) added (do not mutate the original).

    >>> task2_add_key({0: 10, 1: 20}, 2, 30)
    {0: 10, 1: 20, 2: 30}
    """
    out = d.copy()
    out[key] = value
    return out


# Task 3: Concatenate multiple dictionaries
def task3_concat_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Concatenate multiple dicts into a NEW dict.

    >>> dic1 = {1: 10, 2: 20}; dic2 = {3: 30, 4: 40}; dic3 = {5: 50, 6: 60}
    >>> task3_concat_dicts(dic1, dic2, dic3)
    {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60}
    """
    # Python 3.9+ можно так: return dicts[0] | dicts[1] | dicts[2]
    # (The dictionary merge operator was added in PEP 584). :contentReference[oaicite:1]{index=1}
    out: Dict[Any, Any] = {}
    for d in dicts:
        out.update(d)
    return out


# Task 4: Generate a dictionary with squares (1..n)
def task4_squares_dict(n: int) -> Dict[int, int]:
    """
    >>> task4_squares_dict(5)
    {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
    """
    return {x: x * x for x in range(1, n + 1)}
# Dict-comprehension: см. tutorial и PEP 274. :contentReference[oaicite:2]{index=2}


# Task 5: Dictionary of squares (1..15)
def task5_squares_1_to_15() -> Dict[int, int]:
    """
    >>> task5_squares_1_to_15()
    {1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81, 10: 100, 11: 121, 12: 144, 13: 169, 14: 196, 15: 225}
    """
    return {x: x * x for x in range(1, 16)}


# ===========================
# Set Exercises
# ===========================

# Task 6: Create a set
def task6_create_set(items: Iterable[Any] = ()) -> set:
    """
    Create a set (use set() for empty).

    >>> task6_create_set(["apple", "banana", "apple"]) == {"apple", "banana"}
    True
    >>> type(task6_create_set()) is set
    True
    """
    return set(items)
# About sets: tutorial / stdtypes. :contentReference[oaicite:3]{index=3}


# Task 7: Iterate over a set
def task7_iterate_set(s: set, *, sorted_output: bool = True) -> List[Any]:
    """
    Return elements for iteration demo (sorted by default for stable tests).

    >>> task7_iterate_set({"b", "c", "a"})
    ['a', 'b', 'c']
    >>> isinstance(task7_iterate_set({"b", "c", "a"}, sorted_output=False), list)
    True
    """
    return sorted(s) if sorted_output else list(s)
# The sets are unordered; for stable output, you can wrap them in sorted(). :contentReference[oaicite:4]{index=4}


# Task 8: Add member(s) to a set
def task8_add_members(s: set, *members: Any) -> set:
    """
    Add multiple members; returns NEW set.

    >>> task8_add_members({1, 2}, 3, 4) == {1, 2, 3, 4}
    True
    """
    out = s.copy()
    out.update(members)  # add from any iterable
    return out
# Set methods: add/update, etc. See reference guides. :contentReference[oaicite:5]{index=5}


# Task 9: Remove item(s) from a set
def task9_remove_items(s: set, *items: Any, strict: bool = False) -> set:
    """
    Remove items from set; strict=True uses remove() (KeyError if missing),
    else uses discard() (quietly ignores the absence). Returns NEW set.

    >>> task9_remove_items({"apple", "banana", "cherry"}, "banana")
    {'apple', 'cherry'}
    >>> task9_remove_items({"x"}, "y")  # safely (discard)
    {'x'}
    """
    out = s.copy()
    for x in items:
        if strict:
            out.remove(x)
        else:
            out.discard(x)
    return out
# Difference between remove and discard: discard does not throw an error, remove does. :contentReference[oaicite:6]{index=6}


# Task 10: Remove an item if present in the set
def task10_remove_if_present(s: set, item: Any) -> set:
    """
    Remove item if present (using discard). Returns NEW set.

    >>> task10_remove_if_present({1, 2, 3}, 4) == {1, 2, 3}
    True
    >>> task10_remove_if_present({1, 2, 3}, 3) == {1, 2}
    True
    """
    out = s.copy()
    out.discard(item)
    return out
# discard is safe if the element does not exist. :contentReference[oaicite:7]{index=7}


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
