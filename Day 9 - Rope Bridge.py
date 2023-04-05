"""Day 9: Rope Bridge."""
import time
from dataclasses import dataclass, field


@dataclass
class Knot:
    """A simple dataclass."""

    x: int
    y: int
    _locations: set[tuple[int, ...]] = field(default_factory=set)

    def add_current_location(self) -> None:
        """Adds current location to set of visited locations."""
        self._locations.add((self.x, self.y))

    def nr_locations(self) -> int:
        """ Return the nr of locations visited (so far) by this knot."""

        return len(self._locations)


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
                  knot_idxs_to_watch: tuple[int, ...]) -> None:
    """Execute a step in the given direction and after each step move each of
    the tails (if necessary) to keep them in touch with their predecessor."""

    _move_knot(knots[0], direction)

    for i in range(1, len(knots)):
        _follow(knots[i - 1], knots[i])

    for knot_idx in knot_idxs_to_watch:
        knots[knot_idx].add_current_location()


def _execute_steps(instruction: str,
                   knots: tuple[Knot, ...],
                   knot_idxs_to_watch: tuple[int, ...]) -> None:
    """Execute a single instruction (= one or more steps). This is done by
    sequentially executing each required step (all in the same direction)."""

    direction, steps = instruction.split()
    for _ in range(int(steps)):
        _execute_step(direction, knots, knot_idxs_to_watch)


def get_nr_locations(instructions: list[str],
                     nr_knots: int,
                     knot_idxs_to_watch: tuple[int, ...]) -> tuple[int, ...]:
    """Return the nr of locations visited by the last knot in a sequence of
    nr_knots. This is calculated by sequentially executing all (move)
    instructions."""

    knots = tuple(Knot(0, 0) for _ in range(nr_knots))

    for instruction in instructions:
        _execute_steps(instruction, knots, knot_idxs_to_watch)

    return tuple(knots[knot_idx].nr_locations()
                 for knot_idx in knot_idxs_to_watch)


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

    solution_1, solution_2 = get_nr_locations(instructions,
                                              nr_knots=10,
                                              knot_idxs_to_watch=(1, 9))

    stop = time.perf_counter_ns()

    assert solution_1 == 6357
    print(f"Day 9 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 2627
    print(f"Day 9 part 2: {part_2} {solution_2:_}")

    print(f"Day 9 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
