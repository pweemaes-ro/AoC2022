"""Utility functions for sets."""
from collections.abc import Sequence
from functools import reduce
from typing import TypeVar

T = TypeVar("T")


def union_all(sets: Sequence[set[T]]) -> set[T]:
    """Return the union of all sets in the sequence"""
    return reduce(lambda s1, s2: s1.union(s2), sets)


def intersect_all(sets: Sequence[set[T]]) -> set[T]:
    """Return the intersection of all sets in the sequence"""
    return reduce(lambda s1, s2: s1.intersection(s2), sets)


if __name__ == "__main__":
    pass
