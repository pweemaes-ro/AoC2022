"""Utility functions for manipulating matrices."""
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def transpose(matrix: list[list[T]]) -> list[list[T]]:
    """Create and return a new matrix that is the transpose ot 'matrix'. Note
    that the matrix needn't be square."""

    if matrix == [[]]:
        return [[]]

    return [[*items] for items in zip(*matrix)]


def transpose_strings(strings: list[str]) -> list[str]:
    """Return transposed list of strings (i.e.
    ['abc',    ['ad',
     'def'] ->  'be',
                'cf']."""

    if len(strings) == 0:
        return []

    return [''.join(chars) for chars in zip(*strings)]


def rotate_90_strings(strings: list[str], *, clockwise: bool = True) \
        -> list[str]:
    """Return a 90 degrees rotation of the matrix/."""

    if len(strings) == 0:
        return []

    if clockwise:
        return [''.join(chars) for chars in zip(*strings[::-1])]
    else:
        return [''.join(chars) for chars in zip(*strings)][::-1]


def rotate_90(matrix: Sequence[Sequence[T]], *, clockwise: bool = True) \
        -> list[list[T]]:
    """Return a 90 degrees rotation of the matrix/."""

    if matrix == [[]]:
        return [[]]

    if clockwise:
        return [[*items] for items in zip(*matrix[::-1])]
    else:
        return [[*items] for items in zip(*matrix)][::-1]


if __name__ == "__main__":
    def p_print(matrix: Sequence[Sequence[T]]) -> None:
        """Kind of pretty print..."""
        for row in matrix:
            print(row)
        print()

    # Test transpose strings
    s = ['abc', 'def']
    p_print(s)

    t = transpose_strings(s)
    p_print(t)
    assert t == ['ad', 'be', 'cf']

    u = transpose_strings(t)
    p_print(u)
    assert u == s

    # Test rotation of strings over 90 degrees
    s_r = rotate_90_strings(s)
    p_print(s_r)
    assert s_r == ['da', 'eb', 'fc']

    s_r_c = rotate_90_strings(s, clockwise=False)
    p_print(s_r_c)
    assert s_r_c == ['cf', 'be', 'ad']

    # Test transpose
    i = [[1, 2, 3], [4, 5, 6]]
    p_print(i)

    j = transpose(i)
    p_print(j)
    assert j == [[1, 4], [2, 5], [3, 6]]

    k = transpose(j)
    p_print(k)
    assert k == i

    # Test rotation over 90 degrees
    i_r = rotate_90(i)
    p_print(i_r)
    assert i_r == [[4, 1], [5, 2], [6, 3]]

    i_r_c = rotate_90(i, clockwise=False)
    p_print(i_r_c)
    assert i_r_c == [[3, 6], [2, 5], [1, 4]]
