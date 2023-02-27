"""Day 1: Calorie Counting"""
import time
from heapq import nlargest
from typing import IO, Generator


def get_elf_calories(input_file: IO) -> Generator[int, None, int]:
    """Return a generator that yields calories per elf."""

    while True:
        calories = 0
        while (line := input_file.readline()) != '' and line != '\n':
            calories += int(line)

        if calories:
            yield calories
        else:
            return 0


def get_all_elf_calories(filename: str) -> list[int]:
    """Return a list of calories per elf."""

    with open(filename) as input_file:
        return [*get_elf_calories(input_file)]


def main():
    """Solve the problems."""

    part_1 = "Find the Elf carrying the most Calories. How many total " \
             "Calories is that Elf carrying?"
    part_2 = "Find the top three Elves carrying the most Calories. How many " \
             "Calories are those Elves carrying in total?"

    start = time.perf_counter_ns()

    top_n = nlargest(3, get_all_elf_calories("input_files/day1.txt"))

    solution_1 = top_n[0]
    assert solution_1 == 75501
    print(f"Day 1 part 1: {part_1} {solution_1}")

    solution_2 = sum(top_n)
    assert solution_2 == 215594
    print(f"Day 1 part 2: {part_2} {solution_2}")

    stop = time.perf_counter_ns()
    print(f'Day 1 took {(stop - start) * 10 ** -6:.3f} ms')

if __name__ == '__main__':
    main()
