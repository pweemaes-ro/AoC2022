"""Day 11: Monkey in the Middle."""
from __future__ import annotations
import operator
import time
from dataclasses import dataclass, field
from functools import wraps
from heapq import nlargest
from io import StringIO
from math import prod, floor
from queue import Queue
from typing import IO
from collections.abc import Callable


@dataclass
class Item:
    """An item."""

    # The worry level is set when reading the data. In part 1 the worry-level
    # is recalculated and updated whenever the item is inspected, and the test
    # is performed on the actual worry level. This works for part 1 since
    # there are only 20 steps, so the worry level does not get too huge. Since
    # part 1 involves floor(worry-level / 3) and I know of no way to solve (if
    # at all solvable):
    #   if n % p = a then floor(n / 3) % p = ...,
    # this is for now the best I can do...
    worry_level: int

    # current_modulos is used in part 2 only. It has as keys the primes from 2
    # to 19, and for each key it has 0 <= value < key, being the item's
    # starting value modulo that prime. Each time a monkey processes an item,
    # a 'virtual' operation is performed ('virtual', since in part 2 we don't
    # calculate the (huge) new worry level, but only the new worry level's
    # prime modulo's.). The following simple theorems allow for that:
    #   if n % p = a then (n * x) % p = (a * (n % p)) % p
    #   if n % p = a then (n + x) % p = (a + (n % p)) % p
    current_modulos: dict[int, int] = field(default_factory=dict)  # part 2

    def set_initial_modulos(self) -> None:
        """Initializes the modulos for the current value (supposedly the
        starting value)."""

        self.current_modulos = {p: self.worry_level % p
                                for p in (2, 3, 5, 7, 11, 13, 17, 19, 23)}


Operation = Callable[[int, int], int]


@dataclass
class Monkey:
    """Represents a monkey, holding items etc."""

    monkey_id: int
    items: Queue[Item] = field()
    operation: Operation
    test_divisor: int       # divisibility by this nr determines destination
    on_success: int         # destination if divisible by test_divisor
    on_fail: int            # destination if NOT divisible by test_divisor
    inspection_count: int = 0   # How many items did this monkey inspect?

    def get_item_destination(self, item: Item) -> int:
        """Return the destination for the item using part 2 calculations."""

        # TODO: The name of this method is misleading, since it does more than
        #       just returning the destination. It also UPDATES the modulos.

        for prime, current_modulo in item.current_modulos.items():
            item.current_modulos[prime] = self.operation(prime, current_modulo)

        divisible = item.current_modulos[self.test_divisor] == 0
        return self.on_success if divisible else self.on_fail

    def get_item_destination_part_1(self, item: Item) -> int:
        """Return the destination for the item using part 1 calculations."""

        # TODO: The name of this method is misleading, since it does more than
        #       just returning the destination. It also DETERMINES the
        #       destination after MODIFYING the worry level.

        item.worry_level = self.operation(0, item.worry_level)
        item.worry_level = floor(item.worry_level / 3)

        divisible = (item.worry_level % self.test_divisor) == 0

        return self.on_success if divisible else self.on_fail


def _operation_add(term: int) -> Operation:
    """Return a function that takes n and prime as params, and returns
    a) if not prime: n is interpreted as a number and the function returns the
       sum (n + term) (in solving part 1),
    b) else: n is interpreted as the current value of worry level mod prime
       and the functon returns (n + term) modulo prime, being the value of
       worry level modulo prime had we done the actual addition on worry level
       (in solving part 2)."""

    @wraps(_operation_add)
    def _inner(prime: int, n: int) -> int:
        result = n + term
        if prime:
            result %= prime
        return result

    return _inner


def _operation_mul_by(factor: int) -> Operation:
    """Return a function that takes prime and n as params, and returns
    a) if not prime: n is interpreted as a number and the function returns the
       product (n * term) (in solving part 1),
    b) else: n is interpreted as the current value of worry level mod prime
       and the functon returns (n * term) modulo prime, being the value of
       worry level modulo prime had we done the actual multiplication on worry
       level (in solving part 2)."""

    @wraps(_operation_mul_by)
    def _inner(prime: int, n: int) -> int:
        result = n * factor
        if prime:
            result %= prime
        return result

    return _inner


def _operation_square(prime: int, n: int) -> int:
    """Return a function that takes prime and n as params, and returns
    a) if not prime: n is interpreted as a number and the function returns the
       square n ** 2 (in solving part 1)
    b) else: n is interpreted as the current value of worry level mod prime
       and the functon returns (n ** 2) modulo prime, being the value of worry
       level modulo prime had we done the actual squaring on worry level (in
       solving part 2)."""

    result = n * n
    if prime:
        result %= prime
    return result


def _line_to_id(line: str) -> int:
    """Convert line to monkey id. Example:
    'Monkey 0:\n' -> 0
    If EOF then -1 is returned."""

    if not line:
        return -1

    return int(line.split()[-1][:-1])


def _line_to_starting_values(line: str) -> Queue[Item]:
    """Reaa starting values from line, convert to ints and put it in a Queue.
    Return the queue."""

    #     """Convert line to list of ints. Example:
    #     '  Starting items: 73, 77\n' -> [73, 77]
    start_values = [int(i) for i in line.split(":")[-1].split(",")]

    # put the ints in a queue of Item objects, and for each item also set the
    # initial modulo's for all primes from 2 to 19.
    items_queue: Queue[Item] = Queue()
    for initial_worry_level in start_values:
        item = Item(worry_level=initial_worry_level)
        item.set_initial_modulos()
        items_queue.put(item)

    return items_queue


def _line_to_operation(line: str) -> Operation:
    """Convert line to operation lambda. Example:
    '  Operation: new = old * 5\n' returns _add(5)."""

    description, new, equals, old, _operator, var = line.split()
    if _operator == "+":
        if var == "old":    # new = old + old = old * 2
            return _operation_mul_by(2)
        else:               # new = old + n     (n = int(var))
            return _operation_add(int(var))
    elif _operator == "*":
        if var == "old":    # new = old * old
            return _operation_square
        else:               # new = old * n     (n = int(var))
            return _operation_mul_by(int(var))
    else:
        raise ValueError(f"Unexpected operator '{operator}'")


def _line_to_test_divisor(line: str) -> int:
    """Convert line to test lambda. Example:
      'Test: divisible by 11\n' -> lambda: x: x % 11 == 0"""

    # *_, param = line.split()
    return int(line.split()[-1])


def _line_to_destination(line: str) -> int:
    """Convert line to test lambda. Example:
    '    If true: throw to monkey 6\n' -> 6
    '    If false: throw to monkey 3\n' -> 3"""

    return int(line.split()[-1])


def _read_monkey(data_file: IO) -> Monkey | None:
    """Read and return a single Monkey from data file. Return None if no more
    monkeys to read."""

    monkey_id = _line_to_id(data_file.readline())
    if monkey_id == -1:     # EOF, no more monkeys
        return None

    items_queue = _line_to_starting_values(data_file.readline())
    operation = _line_to_operation(data_file.readline())
    test_divisor = _line_to_test_divisor(data_file.readline())
    succes_destination = _line_to_destination(data_file.readline())
    fail_destination = _line_to_destination(data_file.readline())
    _ = data_file.readline()

    return Monkey(monkey_id,
                  items_queue,
                  operation,
                  test_divisor,
                  succes_destination,
                  fail_destination)


def read_monkeys(data_file: IO) -> list[Monkey]:
    """Create and return a list of Monkeys from data in data_file."""

    monkeys: list[Monkey] = []

    while monkey := _read_monkey(data_file):
        monkeys.append(monkey)

    return monkeys


def _play_monkey(monkey: Monkey,
                 monkeys: list[Monkey],
                 part_1: bool) -> None:
    """Process all items for give Monkey."""

    while monkey.items.qsize():
        monkey.inspection_count += 1
        item = monkey.items.get()

        if part_1:
            destination = monkey.get_item_destination_part_1(item)
        else:
            destination = monkey.get_item_destination(item)

        monkeys[destination].items.put(item)


def _play_round(monkeys: list[Monkey], part_1: bool) -> None:
    """Play one round, that is, let all monkeys (in order) process the items
    they're holding (in order)."""

    for monkey in monkeys:
        _play_monkey(monkey, monkeys, part_1)


def do_monkey_business(monkeys: list[Monkey],
                       rounds: int,
                       part_1: bool = False) -> int:
    """Process all rounds for all monkeys and return the 'level of monkey
    business' (the product of the top 2 most items inspected amonst all
    monkeys)."""

    for current_round in range(rounds):
        _play_round(monkeys, part_1)

    return prod(nlargest(2, (m.inspection_count for m in monkeys)))


def main() -> None:
    """Solve the puzzle"""

    part_1 = "What is the level of monkey business after 20 rounds of " \
             "stuff-slinging simian shenanigans?"
    part_2 = "Starting again from the initial state in your puzzle input, " \
             "what is the level of monkey business after 10000 rounds?"

    start = time.perf_counter_ns()

    with open("input_files/day11.txt") as input_file:
        lines = input_file.readlines()

    monkeys = read_monkeys(StringIO(''.join(lines)))
    solution_1 = do_monkey_business(monkeys, rounds=20, part_1=True)

    monkeys = read_monkeys(StringIO(''.join(lines)))
    solution_2 = do_monkey_business(monkeys, rounds=10000)

    stop = time.perf_counter_ns()

    assert solution_1 == 56120
    print(f"Day 11 part 1: {part_1} {solution_1}")

    assert solution_2 == 24389045529
    print(f"Day 11 part 2: {part_2} {solution_2}")

    print(f"Day 11 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
