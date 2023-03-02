"""Day 9: Rope Bridge."""
import time
from dataclasses import dataclass


@dataclass
class Knot:
    """A simple hashable (so we can put instances in a set) dataclass."""

    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))


Locations = set[Knot]


def _move_knot(knot: Knot, direction: str) -> None:
    match direction:
        case "L":
            knot.x -= 1
        case "R":
            knot.x += 1
        case "U":
            knot.y += 1
        case "D":
            knot.y -= 1
        case _:
            raise ValueError(f"Unexpected direction '{direction}'")


def _follow(head: Knot, tail: Knot) -> None:
    """The heart of the solution: How should a tail at the given location move
    if it is following the head towards its location?"""

    distance_x = abs(head.x - tail.x)
    distance_y = abs(head.y - tail.y)

    if distance_x < 2 and distance_y < 2:
        return

    avg_x = (head.x + tail.x) // 2
    avg_y = (head.y + tail.y) // 2

    tail.x = avg_x if distance_x == 2 else head.x
    tail.y = avg_y if distance_y == 2 else head.y


def _execute_step(direction: str,
                  knots: tuple[Knot, ...],
                  locations: Locations) -> None:
    """Execute a step in the given direction and after each step move each of
    the tails (if necessary) to keep them in touch with their predecessor."""

    _move_knot(knots[0], direction)
    for i in range(1, len(knots)):
        _follow(knots[i - 1], knots[i])
        locations.add(knots[-1])


def _execute_instruction(instruction: str,
                         knots: tuple[Knot, ...],
                         locations: Locations) -> None:
    """Execute a single instruction. This is done by sequentially executing
    single steps (one up, down, left or right)."""

    direction, steps = instruction.split()
    for _ in range(int(steps)):
        _execute_step(direction, knots, locations)


def get_nr_locations(instructions: list[str], nr_knots: int) -> int:
    """Return the nr of locations visited by the last knot in a sequence of
    nr_knots. This is calculated by sequentially executing all (move)
    instructions."""

    knots = tuple(Knot(0, 0) for _ in range(nr_knots))
    locations_visited = {knots[-1]}

    for instruction in instructions:
        _execute_instruction(instruction, knots, locations_visited)

    return len(locations_visited)


def main() -> None:
    """Solve the puzzle"""

    part_1 = "Simulate your complete hypothetical series of motions. How " \
             "many positions does the tail of the rope visit at least once?"
    part_2 = "Simulate your complete series of motions on a larger rope " \
             "with ten knots. How many positions does the tail of the rope " \
             "visit at least once?"

    start = time.perf_counter_ns()

    with open("input_files/day9.txt") as input_file:
        instructions = input_file.readlines()

    solutions: list[int] = []

    for nr_knots in (2, 10):
        nr_locations = get_nr_locations(instructions, nr_knots)
        solutions.append(nr_locations)

    solution_1, solution_2 = solutions

    stop = time.perf_counter_ns()

    assert solution_1 == 6357
    print(f"Day 9 part 1: {part_1} {solution_1}")

    assert solution_2 == 2627
    print(f"Day 9 part 2: {part_2} {solution_2}")

    print(f"Day 9 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
