"""Reusable stuff..."""
from dataclasses import dataclass
from functools import reduce
from typing import TypeVar
from collections.abc import Sequence
T = TypeVar("T")


def intersect_all(sets: Sequence[set[T]]) -> set[T]:
    """Return the intersection of all sets in the sequence"""
    return reduce(lambda s1, s2: s1.intersection(s2), sets)


def union_all(sets: Sequence[set[T]]) -> set[T]:
    """Return the union of all sets in the sequence"""
    return reduce(lambda s1, s2: s1.union(s2), sets)


def transposed(matrix: list[list[T]]) -> list[list[T]]:
    """Create and return a new matrix that is the transpose ot the matrix
    parameter. Note that the matrix needn't be square."""

    # For empty matrices, both len(matrix) and len(matrix[0]) are 0, so the
    # general approach would result in [], not the required [[]].
    if matrix == [[]]:
        return [[]]

    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


@dataclass
class Coordinate:
    """A simple coordinate class that is hashable (so we can store coordinates
    in a set)."""

    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))


if __name__ == "__main__":
    pass
