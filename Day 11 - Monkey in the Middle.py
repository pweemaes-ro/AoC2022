"""Day 11: Monkey in the Middle."""
from __future__ import annotations

import re
import time
from collections.abc import MutableSequence
from copy import deepcopy
from dataclasses import dataclass, field
from heapq import nlargest
from math import prod, floor
from typing import IO, Callable, TypeAlias, Optional

# type aliases
Operation: TypeAlias = Callable[[int], int]
# Monkey and Item are classes defined below, so use string literals.
InspectionFunc: TypeAlias = Callable[["Monkey", "Item"], int]


@dataclass
class Item:
    """An item."""
    # The worry level is set when reading the data. In part 1 the worry-level
    # is recalculated and updated whenever the item is inspected, and the test
    # is performed on the actual worry level. This works for part 1 since
    # there are only 20 steps, so the worry level does not get too large. Since
    # part 1 involves floor(worry-level / 3) and I know of no way to solve (if
    # at all solvable):
    #   if n % p = a then floor(n / 3) % p = ...,
    # this is for now the best I can do...
    worry_level: int

    # 'modulos' is a dictionary that is used in part 2 only. It has as keys
    # the test divisors, and for each divisor it has a value in the range
    # 0 <= value < divisor. Initially this value is se to
    # (initial worry level modulo divisor. Each time a monkey inspects an
    # item, it is updated using the following simple theorems:
    #   if n % d = a then (n * x) % d = (a * x) % d
    #   if n % d = a then (n + x) % d = (a + x) % d
    # This way we don't need to use the eventually very large worry_levels to
    # determine the destination of an item.
    # UPDATE April 18th 2023: From the solutions on Reddit I conclude that my
    # solution (only storing the modulo's to avoid very large worry levels) is
    # correct, there seems to be NO MATH TRICK to improve any further.
    modulos: dict[int, int] = field(init=False, repr=False, compare=False)


@dataclass
class Monkey:
    """Represents a monkey, holding items etc."""

    monkey_id: int
    items: MutableSequence[Item]
    operation: Operation
    test_divisor: int
    destination_if_test_true: int
    destination_if_test_false: int
    destination_id_func: InspectionFunc = field(init=False)
    inspection_count: int = 0   # How many items did this monkey inspect?

    def inspect_items(self, monkeys: list[Monkey]) -> None:
        """Inspects all items and throws them to other monkeys."""

        self.inspection_count += len(self.items)

        while self.items:
            # Get next item, inspect it and move it to whatever monkey the
            # inspection function tells us to move it to.
            item = self.items.pop(-1)
            destination_id = self.destination_id_func(self, item)
            monkeys[destination_id].items.append(item)

    def set_initial_modulos(self, test_divisors: set[int]) -> None:
        """Set modulos for all items that this monkey is currently
        holding"""

        for item in self.items:
            item.modulos = {test_divisor: item.worry_level % test_divisor
                            for test_divisor in test_divisors}


def get_destination_id_1(monkey: Monkey, item: Item) -> int:
    """Return destination (monkey id) that the item is thrown to after
    inspection, using the algorithm for part 1."""

    item.worry_level = floor(monkey.operation(item.worry_level) / 3)

    # Part 1 requires only 20 rounds, so the numbers remain relatively small,
    # so we can do the real calculations
    if item.worry_level % monkey.test_divisor == 0:
        return monkey.destination_if_test_true
    else:
        return monkey.destination_if_test_false


def get_destination_id_2(monkey: Monkey, item: Item) -> int:
    """Return destination (monkey id) that the item is thrown to after
    inspection, using the algorithm for part 2."""

    # Update modulos for ALL divisors (since this item may end up in the hands
    # of any of the monkeys)! I'm not aware of any more clever method of
    # calculating an item's destination while avoiding huge numbers.
    for divisor, current_modulo in item.modulos.items():
        item.modulos[divisor] = monkey.operation(current_modulo) % divisor

    # Now determine divisibility and destination.
    if item.modulos[monkey.test_divisor] == 0:
        return monkey.destination_if_test_true
    else:
        return monkey.destination_if_test_false


def _get_items(line: str) -> MutableSequence[Item]:
    """Return a list of items with initial worry levels set from input line.
    Example:
    '  Starting items: 60, 76, 90, 63, 86, 87, 89\n'
    returns a list of items with initial worry levels 60, 76, 90, 63, 86, 87
    and 89, respectu=ively."""

    return [Item(worry_level=int(start_value))
            for start_value in re.findall(r"\d+", line)]


def _get_operation(line: str) -> Operation:
    """Evaluate line and return an operation (lambda with int param and int
    return value)."""

    *_, operator, operand = line.split()
    match operator, operand:
        case "+", "old":    # Note: 'new = old + old' is not in my input...
            return lambda _old_value: _old_value + _old_value
        case "+", operand:
            return lambda _old_value: _old_value + int(operand)
        case "*", "old":
            return lambda _old_value: _old_value * _old_value
        case "*", operand:
            return lambda _old_value: _old_value * int(operand)
        case _, _:
            raise ValueError(f"Unexpected {operator=}, {operand=}")

    return lambda _old_value: 0


def _get_int(line: str) -> int:

    all_ints = re.findall(r"\d+", line)

    if all_ints:
        return int(all_ints[0])
    else:
        return -1


def _read_monkey(data_file: IO[str]) -> Optional[tuple[Monkey, Monkey]]:
    """Return a tuple of two identical Monkeys (identical, but independent,
    that is, changes in one do not affect the other). Return None if no more
    monkeys to read."""

    if (monkey_id := _get_int(data_file.readline())) == -1:
        return None

    items = _get_items(data_file.readline())
    operation = _get_operation(data_file.readline())
    test_divisor = _get_int(data_file.readline())
    destination_if_test_true = _get_int(data_file.readline())
    destination_if_test_false = _get_int(data_file.readline())
    _ = data_file.readline()    # Skip empty line

    monkey_1 = Monkey(monkey_id,
                      items,
                      operation,
                      test_divisor,
                      destination_if_test_true,
                      destination_if_test_false)
    monkey_2 = Monkey(monkey_id,
                      deepcopy(items),  # NEED deepcopy only here!
                      operation,
                      test_divisor,
                      destination_if_test_true,
                      destination_if_test_false)

    return monkey_1, monkey_2


def read_monkeys(data_file: IO[str]) -> tuple[list[Monkey], list[Monkey]]:
    """Return tuple of two lists of Monkeys from data in data_file."""

    monkey_lists: tuple[list[Monkey], list[Monkey]] = ([], [])

    while monkeys := _read_monkey(data_file):
        monkey_lists[0].append(monkeys[0])
        monkey_lists[1].append(monkeys[1])

    return monkey_lists


def _play_round(monkeys: list[Monkey]) -> None:
    """Play one round, that is, let all monkeys (in order) process the items
    they're holding (in order)."""

    for monkey in monkeys:
        monkey.inspect_items(monkeys)


def do_monkey_business(monkeys: list[Monkey],
                       rounds: int) -> int:
    """Process all rounds for all monkeys and return the 'level of monkey
    business' (the product of the top 2 most items inspected amongst all
    monkeys)."""

    for _ in range(rounds):
        _play_round(monkeys)

    return prod(nlargest(2, (m.inspection_count for m in monkeys)))


def set_inspection_function(monkeys: list[Monkey],
                            inspection_func: InspectionFunc) -> None:
    """Set the inspection function for all monkeys in 'monkeys'."""

    for monkey in monkeys:
        monkey.destination_id_func = inspection_func


def set_initial_modulos(monkeys: list[Monkey]) -> None:
    """Sets the initial modulos for all items for all monkeys. The initial
    modulo is calculated for each test divisor for each item, using the
    current (initial) worry_level. The test divisors are read from the monkey
    data structs."""

    test_divisors = set(monkey.test_divisor for monkey in monkeys)

    for monkey in monkeys:
        monkey.set_initial_modulos(test_divisors)


def main() -> None:
    """Solve the puzzle"""

    part_1 = "What is the level of monkey business after 20 rounds of " \
             "stuff-slinging simian shenanigans?"
    part_2 = "Starting again from the initial state in your puzzle input, " \
             "what is the level of monkey business after 10000 rounds?"

    start = time.perf_counter_ns()

    with open("input_files/day11.txt") as input_file:
        monkeys_1, monkeys_2 = read_monkeys(input_file)

    set_inspection_function(monkeys_1, get_destination_id_1)
    solution_1 = do_monkey_business(monkeys_1, rounds=20,)

    set_initial_modulos(monkeys_2)
    set_inspection_function(monkeys_2, get_destination_id_2)
    solution_2 = do_monkey_business(monkeys_2, rounds=10_000)

    stop = time.perf_counter_ns()

    assert solution_1 == 56120
    print(f"Day 11 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 24389045529
    print(f"Day 11 part 2: {part_2} {solution_2:_}")

    print(f"Day 11 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
