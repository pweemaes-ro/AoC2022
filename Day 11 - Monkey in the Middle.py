"""Day 11: Monkey in the Middle."""
import operator
import time
from dataclasses import dataclass, field
from heapq import nlargest
from io import StringIO
from math import prod, floor
from queue import Queue
from typing import Callable, IO

primes = (2, 3, 5, 7, 11, 13, 17, 19, 23)


@dataclass
class Item:
    """An item."""

    # The worry level is set when reading the data.
    # - In part 1 the worry-level is recalculated and updated whenever the
    #   item is moved.
    # - In part 2 the item worry-level is never changed, since we can always
    #   de the divisibility test without calculating the new value (using
    #   simple module arithmetic:
    #   if n % p = a then (n * x) % p = (a * (n % p)) % p
    #   if n % p = a then (n + x) % p = (a + (n % p)) % p
    # Notice that part 1 does floor(n / 3). I have no idea if or how the
    # following could be completed...
    #   if n % p = a then floor(n / x) % p = ...

    worry_level: int
    current_modulos: dict[int, int] = field(default_factory=dict)  # part 2

    def set_modulos(self) -> None:
        """Initializes the modulos for the current value"""
        self.current_modulos = {p: self.worry_level % p for p in primes}


@dataclass
class Monkey:
    """Represents a monkey, holding items etc."""

    monkey_id: int
    items: Queue = field()
    operation: Callable[[int, int], int]
    test_divisor: int
    on_success: int
    on_fail: int
    inspection_count: int = 0

    def get_item_destination(self, item: Item) -> int:
        """Return the destination for the item using part 2 calculations."""

        item.current_modulos = {k: self.operation(v, k)
                                for k, v in item.current_modulos.items()}

        divisible = (item.current_modulos[self.test_divisor] == 0)
        return self.on_success if divisible else self.on_fail

    def get_item_destination_part_1(self, item: Item) -> int:
        """Return the destination for the item using part 1 calculations."""

        item.worry_level = self.operation(item.worry_level, -1)
        item.worry_level = floor(item.worry_level / 3)

        divisible = (item.worry_level % self.test_divisor) == 0

        return self.on_success if divisible else self.on_fail


def _get_id(line: str) -> int:
    """Convert line to monkey id. Example:
    'Monkey 0:\n' -> 0"""

    return int(line.split()[1][:-1])


def _get_values(line: str) -> list[int]:
    """Convert line to items. Example:
    '  Starting items: 73, 77\n' -> [73, 77]"""

    colon_pos = line.find(":")
    items_str = line[colon_pos + 2:-1]
    item_strs = items_str.split(",")
    return [*map(int, item_strs)]


def _add_to(term):
    def _inner(n, p) -> int:
        if p == -1:
            return n + term
        else:
            return (n + (term % p)) % p
    return _inner


def _mul_by(factor):
    def _inner(n, p) -> int:
        if p == -1:
            return n * factor
        else:
            return (n * (factor % p)) % p
    return _inner


def _square(n, p) -> int:
    if p == -1:
        return n * n
    else:
        return (n * n) % p


def _get_operation(line: str) -> Callable[[int], int]:
    """Convert line to operation lambda. Example:
    '  Operation: new = old * 5\n' -> lambda x: x * 5"""

    description, new, equals, old, _operator, var = line.split()
    if _operator == "+":
        if var == "old":    # new = old + old
            return _mul_by(2)
        else:               # new = old + int(var)
            return _add_to(int(var))
    elif _operator == "*":
        if var == "old":    # new = old * old (= old ** 2)
            return _square
        else:
            return _mul_by(int(var))
    else:
        raise ValueError(f"Unexpected operator '{operator}'")


def _get_test_divisor(line) -> int:
    """Convert line to test lambda. Example:
      'Test: divisible by 11\n' -> lambda: x: x % 11 == 0"""

    # *_, param = line.split()
    return int(line.split()[-1])


def _get_destination(line) -> int:
    """Convert line to test lambda. Example:
    '    If true: throw to monkey 6\n' -> 6
    '    If false: throw to monkey 3\n' -> 3"""

    *_, destination = line.split()
    return int(destination)


def read_monkey_data(data_file: IO) -> dict[int, Monkey]:
    """Create and return monkeys from data in data_file."""

    monkeys: dict[int, Monkey] = dict()
    while True:
        line = data_file.readline()
        if not line:
            return monkeys
        monkey_id = _get_id(line)

        line = data_file.readline()
        start_values = _get_values(line)
        items_queue = Queue()
        for value in start_values:
            item = Item(worry_level=value)
            item.set_modulos()
            items_queue.put(item)

        line = data_file.readline()
        operation = _get_operation(line)

        line = data_file.readline()
        test_divisor = _get_test_divisor(line)

        line = data_file.readline()
        succes_destination = _get_destination(line)

        line = data_file.readline()
        fail_destination = _get_destination(line)

        _ = data_file.readline()

        monkey = Monkey(monkey_id,
                        items_queue,
                        operation,
                        test_divisor,
                        succes_destination,
                        fail_destination)
        monkeys[monkey_id] = monkey


def _play_monkey(monkey_id, monkeys: dict[int, Monkey], part_1: bool) -> None:
    """Process all items for monkey with given id."""

    monkey = monkeys[monkey_id]

    while monkey.items.qsize():
        monkey.inspection_count += 1

        item = monkey.items.get()

        if part_1:
            destination = monkey.get_item_destination_part_1(item)
        else:
            destination = monkey.get_item_destination(item)

        monkeys[destination].items.put(item)


def _play_round(monkeys: dict[int, Monkey], part_1: bool) -> None:
    """Play one round, that is, let all monkeys (in order) process the items
    they're holding (in order)."""

    nr_monkeys = len(monkeys)

    for monkey_id in range(nr_monkeys):
        _play_monkey(monkey_id, monkeys, part_1)


def do_monkey_business(monkeys: dict[int, Monkey],
                       rounds: int,
                       part_1: bool = False) -> int:
    """Process all rounds for all monkeys and return the 'level of monkey
    business (the product of the top 2 nr of items inspected amonst all
    monkeys)."""

    for current_round in range(rounds):
        _play_round(monkeys, part_1)

    return prod(nlargest(2, (m.inspection_count
                             for m in monkeys.values())))


def main() -> None:
    """Solve the puzzle"""

    part_1 = "What is the level of monkey business after 20 rounds of " \
             "stuff-slinging simian shenanigans?"
    part_2 = "Starting again from the initial state in your puzzle input, " \
             "what is the level of monkey business after 10000 rounds?"

    start = time.perf_counter_ns()

    with open("input_files/day11.txt") as input_file:
        lines = input_file.readlines()

    monkeys = read_monkey_data(StringIO(''.join(lines)))
    solution_1 = do_monkey_business(monkeys, rounds=20, part_1=True)

    monkeys = read_monkey_data(StringIO(''.join(lines)))
    solution_2 = do_monkey_business(monkeys, rounds=10000)

    stop = time.perf_counter_ns()

    assert solution_1 == 56120
    print(f"Day 11 part 1: {part_1} {solution_1}")

    assert solution_2 == 24389045529
    print(f"Day 11 part 2: {part_2} {solution_2}")

    print(f"Day 11 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
