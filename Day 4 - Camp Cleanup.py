"""Day 4: Camp Cleanup."""
import re
import time
from collections.abc import Sequence
from typing import TypeAlias

# type alias
RangePair: TypeAlias = Sequence[int]


def is_overlap(range_pair: RangePair) -> bool:
    """range_pair is assumed to be a sequence of 4 integers p <= q, r <= s.
    Return True if range(p, q) and range(r, s) overlap, else returns False."""

    p, q, r, s = range_pair

    return (r <= p <= s) or (p <= r <= q)


def is_containment(range_pair: RangePair) -> bool:
    """range_pair is assumed to be a sequence of 4 integers p <= q, r <= s.
    Return True if range(p, q) contains range(r, s) or range(r, s) contains
    range(p, q), else returns False."""

    p, q, r, s = range_pair

    return (p >= r and q <= s) or (r >= p and s <= q)


def get_range_pair(line: str) -> RangePair:
    """Convert integers in line to a RangePair (Sequence of four ints)."""

    return tuple(map(int, re.findall(r"\d+", line)))


def main() -> None:
    """Solve the puzzle."""

    part_1 = "In how many assignment pairs does one range fully contain the " \
             "other?"
    part_2 = "In how many assignment pairs do the ranges overlap?"

    start = time.perf_counter_ns()

    with open("input_files/day4.txt") as file:
        lines = file.readlines()

    range_pairs = tuple(get_range_pair(line) for line in lines)

    containment = overlap = 0
    for range_pair in range_pairs:
        if is_containment(range_pair):
            containment += 1
        elif is_overlap(range_pair):
            overlap += 1

    solution_1 = containment
    solution_2 = containment + overlap  # containment implies overlap!

    stop = time.perf_counter_ns()

    assert solution_1 == 503
    print(f"Day 4 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 827
    print(f"Day 4 part 2: {part_2} {solution_2:_}")

    print(f"Day 4 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
