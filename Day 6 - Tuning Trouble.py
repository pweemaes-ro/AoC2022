"""Day 6: Tuning Trouble"""
import time


def find_distinct_chars(text: str, start: int, size: int) -> int:
    """Return pos after first occurance of 'size' different chars in text.
    """

    for i in range(start, len(text) - size):
        if len(set(text[i: i + size])) == size:
            return i + size
    return -1


def main() -> None:
    """Solve the puzzle."""

    # Note: My solution was slower, worked with many file.read(1) calls and
    #       pop()/append() to create chunks of desired size. I took the idea to
    #       work with one file.read() from reddit AoC forum.
    part_1 = "How many characters need to be processed before the first " \
             "start-of-packet marker is detected?"
    part_2 = "How many characters need to be processed before the first " \
             "start-of-message marker is detected?"

    start = time.perf_counter_ns()

    with open("input_files/day6.txt") as input_file:
        text = input_file.read()
        solution_1 = find_distinct_chars(text, 0, 4)
        solution_2 = find_distinct_chars(text, solution_1 - 4, 14)

    stop = time.perf_counter_ns()

    assert solution_1 == 1175
    print(f"Day 6 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 3217
    print(f"Day 6 part 2: {part_2} {solution_2:_}")

    print(f"Day 6 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
