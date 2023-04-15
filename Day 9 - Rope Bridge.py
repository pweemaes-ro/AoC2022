"""Day 9: Rope Bridge."""
import time
from dataclasses import dataclass, field


@dataclass
class Knot:
    """A simple dataclass."""

    x: int      # Current x coordinate
    y: int      # Current y coordinate
    visited_locations: set[tuple[int, ...]] = field(default_factory=set)

    def update_visited_locations(self) -> None:
        """Add current knot location to the visited locatiosn."""

        self.visited_locations.add((self.x, self.y))


def _move_knot(knot: Knot, direction: str) -> None:
    """Modify knot coordinates to reflect moving one step in the given
    direction"""

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
    """The heart of the solution: How should the tail move if it is stay
    connected to the head?"""

    distance_x = abs(head.x - tail.x)
    distance_y = abs(head.y - tail.y)

    if distance_x < 2 and distance_y < 2:
        # Tails is still connected, no need to move.
        return

    # If the distance in a dimension is two, move to head and tail average
    # coordinate that dimension, that is, go one left/right (for x dimension)
    # or one up/down (for y dimension) in the direction of head. Else move to
    # same coordinate as head.
    tail.x = (head.x + tail.x) // 2 if distance_x == 2 else head.x
    tail.y = (head.y + tail.y) // 2 if distance_y == 2 else head.y


def _execute_step(direction: str,
                  knots: tuple[Knot, ...],
                  knot_idxs_to_watch: tuple[int, ...]) -> None:
    """Execute a step in the given direction and after each step move each of
    the tails (if necessary) to keep them in touch with their predecessor."""

    # Move the head (first knot) in the given direction.
    _move_knot(knots[0], direction)

    # The other knots, one by one, follow the knot just before them...
    for i in range(1, len(knots)):
        _follow(knots[i - 1], knots[i])

    # Keep track of the visited locations for the specified knots.
    for knot_idx in knot_idxs_to_watch:
        knots[knot_idx].update_visited_locations()


def _execute_instruction(instruction: str,
                         knots: tuple[Knot, ...],
                         knot_idxs_to_watch: tuple[int, ...]) -> None:
    """Execute a single instruction (= one or more steps). This is done by
    sequentially executing each required step (all in the same direction)."""

    direction, nr_steps = instruction.split()

    for _ in range(int(nr_steps)):
        _execute_step(direction, knots, knot_idxs_to_watch)


def execute_instructions(instructions: list[str],
                         knots: tuple[Knot, ...],
                         knot_idxs_to_watch: tuple[int, ...]) -> None:
    """Execute the instructions."""

    for instruction in instructions:
        _execute_instruction(instruction, knots, knot_idxs_to_watch)


def get_nr_locations(knots: tuple[Knot, ...],
                     knot_idxs_to_watch: tuple[int, ...]) -> tuple[int, ...]:
    """Return the nr of locations visited by the knots whose ids are in
    knot_idxs_to_watch."""

    return tuple(len(knots[knot_idx].visited_locations)
                 for knot_idx in knot_idxs_to_watch)


def create_knots(nr_knots: int) -> tuple[Knot, ...]:
    """Return a tuple of 'nr_knots' knots, initially located at (0,0)."""

    return tuple(Knot(0, 0) for _ in range(nr_knots))


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

    knots = create_knots(10)
    knot_idxs_to_watch = (1, 9)
    execute_instructions(instructions, knots, knot_idxs_to_watch)
    solution_1, solution_2 = get_nr_locations(knots, knot_idxs_to_watch)

    stop = time.perf_counter_ns()

    assert solution_1 == 6357
    print(f"Day 9 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 2627
    print(f"Day 9 part 2: {part_2} {solution_2:_}")

    print(f"Day 9 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
