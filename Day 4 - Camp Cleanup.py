"""Day 4: Camp Cleanup."""
import time


def is_overlap(range_pair: list[int]) -> bool:
    """Return True if one range overlaps the other. A range is a
    tuple(first, last) and one tuple overlaps another iif
    - start first between start second and stop second,
    OR
    - start second between start first and stop first,"""

    start_first, stop_first, start_second, stop_second = range_pair

    return (start_second <= start_first <= stop_second) or \
        (start_first <= start_second <= stop_first)


def is_containment(range_pair: list[int]) -> bool:
    """Return True if one range is contained in the other. A range is a
    tuple(first, last) and one tuple completeley overlaps another iif
    - start first >= start second AND stop first <= stop second,
    OR
    - start second >= start first AND stop second <= stop first."""

    start_first, stop_first, start_second, stop_second = range_pair

    return (start_first >= start_second and stop_first <= stop_second) or \
        (start_second >= start_first and stop_second <= stop_first)


def main():
    """Solve the puzzle."""

    part_1 = "In how many assignment pairs does one range fully contain the " \
             "other?"
    part_2 = "In how many assignment pairs do the ranges overlap?"

    start = time.perf_counter_ns()

    with open("input_files/day4.txt") as file:
        lines = file.readlines()

    # Convert n file lines, with n == 4:
    # 1-93,2-11
    # 26-94,26-94
    # 72-92,48-88
    # 36-37,37-52
    # to a list of n lists of (always) 4 integers
    # [[1, 93, 2, 11],
    #  [26, 94, 26, 94],
    #  [72, 92, 48, 88],
    #  [36, 37, 37, 52]]
    # We use a list-generator expression that for each line from the file:
    # 1. removes last char "\n": line[:len(line) - 1]
    # 2. replaces the "," with "-": replace(",", "-")
    # 3. splits on "-": split("-"), and
    # 4. converts strings from split to ints: int(s) for s in ....split("-").
    lists_of_ints = [
        [int(s)
         for s in line[:len(line) - 1].replace(",", "-").split("-")]
        for line in lines]

    containment = overlap = 0
    for list_of_ints in lists_of_ints:
        if is_containment(list_of_ints):
            containment += 1
        elif is_overlap(list_of_ints):
            overlap += 1

    solution_1 = containment
    solution_2 = containment + overlap

    stop = time.perf_counter_ns()

    assert solution_1 == 503
    print(f"Day 4 part 1: {part_1} {solution_1}")

    assert solution_2 == 827
    print(f"Day 4 part 2: {part_2} {solution_2}")

    print(f"Day 4 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
