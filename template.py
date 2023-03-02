"""Day x: description."""
import time


def main() -> None:
    """Solve the puzzle"""

    part_1 = ""
    part_2 = ""

    start = time.perf_counter_ns()

    ...     # calc the solution

    solution_1 = ...
    solution_2 = ...

    stop = time.perf_counter_ns()

    assert solution_1 == 0
    print(f"Day ... part 1: {part_1} {solution_1}")

    assert solution_2 == 0
    print(f"Day ... part 2: {part_2} {solution_2}")

    print(f"Day ... took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
