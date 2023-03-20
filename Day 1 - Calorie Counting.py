"""Day 1: Calorie Counting"""
import time
from heapq import nlargest
from collections.abc import Generator


def get_elf_calories(filename: str) -> Generator[int, None, None]:
    """Return a generator that yields calories per elf."""

    with open(filename) as input_file:
        while True:
            calories = 0
            while (line := input_file.readline()) and line != "\n":
                calories += int(line)

            if calories:
                yield calories
            else:
                break


def main():
    """Solve the problems."""

    part_1 = "Find the Elf carrying the most Calories. How many total " \
             "Calories is that Elf carrying?"
    part_2 = "Find the top three Elves carrying the most Calories. How many " \
             "Calories are those Elves carrying in total?"

    start = time.perf_counter_ns()

    top_3 = nlargest(3, get_elf_calories("input_files/day1.txt"))

    solution_1 = top_3[0]
    solution_2 = sum(top_3)

    stop = time.perf_counter_ns()

    assert solution_1 == 75501
    print(f"Day 1 part 1: {part_1} {solution_1}")

    assert solution_2 == 215594
    print(f"Day 1 part 2: {part_2} {solution_2}")

    print(f"Day 1 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
