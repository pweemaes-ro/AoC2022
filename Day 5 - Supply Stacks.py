"""Day 5: Supply Stacks"""
import time
from collections.abc import Sequence, Callable
from copy import deepcopy
from typing import TypeAlias

from AoCLib.Miscellaneous import transposed

# type aliases
Stack: TypeAlias = list[str]
Stacks: TypeAlias = list[Stack]
Move: TypeAlias = Sequence[int]


def _stack_row(line: str) -> list[str]:
    """Return a list of labels based on a line. Example: line
    '    [V]     [M] [W] [S]     [Q]'
    is converted to list of (always!) 9 one char strings:
    [' '. 'V', ' ', 'M', 'W', 'S', ' ', 'Q', ' ']
    Notice that 'missing' labels (anywhere) are replaced by ' '."""

    nr_labels = (len(line) + 1) // 4

    labels = [line[i * 4 + 1] for i in range(nr_labels)]
    extra_blanks = [" " for _ in range(9 - nr_labels)]

    return labels + extra_blanks


def create_stacks(lines: Sequence[str]) -> Stacks:
    """Return stacks, created from the data in the file."""

    stack_rows = [_stack_row(stack_line) for stack_line in lines]
    stack_columns = transposed(stack_rows)

    for stack in stack_columns:
        while stack[-1] == ' ':
            stack.pop()

    return stack_columns


def _create_move(move_line: str) -> Move:
    """Return a Move (a tuple(nr_to_move, from_stack_idx, to_stack_idx),
    created from the data in move_line, expected in format 'move <nr_to_move>
    from <from_stack> to <to_stack>'."""

    _, nr_to_move, _, from_stack, _, to_stack = move_line.split(" ")
    # stack idxs are 0 based in code, 1-based in move_line, so subtract 1!
    return int(nr_to_move), int(from_stack) - 1, int(to_stack) - 1


def create_moves(move_lines: Sequence[str]) -> Sequence[Move]:
    """Return a list of Moves created from data in the file."""

    return tuple(_create_move(move_line) for move_line in move_lines)


def _do_move_part_1(stacks: Stacks, move: Sequence[int]) -> None:
    """Executes the move on the stacks."""

    nr_to_move, from_idx, to_idx = move

    _do_move(stacks,
             items_to_move=stacks[from_idx][:-nr_to_move - 1:-1],
             from_idx=from_idx,
             to_idx=to_idx)


def _do_move_part_2(stacks: Stacks, move: Sequence[int]) -> None:
    """Executes the move on the stacks."""

    nr_to_move, from_idx, to_idx = move

    _do_move(stacks,
             items_to_move=stacks[from_idx][-nr_to_move:],
             from_idx=from_idx,
             to_idx=to_idx)


def _do_move(stacks: Stacks,
             items_to_move: list[str], *,
             from_idx: int,
             to_idx: int) \
        -> None:

    stacks[to_idx].extend(items_to_move)
    del stacks[from_idx][-len(items_to_move):]


def do_moves(stacks: Stacks,
             moves: Sequence[Move], *,
             move_function: Callable[[Stacks, Sequence[int]], None]) \
        -> None:
    """Execute all moves on the stacks."""

    for move in moves:
        move_function(stacks, move)


def main() -> None:
    """Solve the puzzle"""

    part_1 = "After the rearrangement procedure completes, what crate ends " \
             "up on top of each stack?"
    part_2 = part_1

    start = time.perf_counter_ns()

    with open("input_files/day5.txt") as input_file:
        lines = input_file.read().splitlines()

    stacks_1 = create_stacks(lines[7::-1])  # Notice the reversed order
    stacks_2 = deepcopy(stacks_1)

    moves = create_moves(lines[10:])

    do_moves(stacks_1, moves, move_function=_do_move_part_1)
    do_moves(stacks_2, moves, move_function=_do_move_part_2)

    solution_1 = "".join(stack[-1] for stack in stacks_1)
    solution_2 = "".join(stack[-1] for stack in stacks_2)

    stop = time.perf_counter_ns()

    assert solution_1 == "CFFHVVHNC"
    print(f"Day 5 part 1: {part_1} {solution_1}")

    assert solution_2 == "FSZWBPTBG"
    print(f"Day 5 part 2: {part_2} {solution_2}")

    print(f"Day 5 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
