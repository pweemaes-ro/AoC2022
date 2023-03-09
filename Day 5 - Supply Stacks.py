"""Day 5: Supply Stacks"""
import time
from copy import deepcopy
from typing import IO

from AoCLib.Miscellaneous import transposed

Stack = list[str]
Stacks = list[Stack]
MultiStacks = tuple[Stacks, ...]
MoveInfo = tuple[int, ...]
MoveInfos = tuple[MoveInfo, ...]


def _line_to_labels(line):
    """Return a list of labels based on a line. Example:
    line "    [J]     [W] [V] [Q] [W] [F]    " is converted to list of labels:
    [" ". "J", " ", "W", "V", "Q", "W", "F", " "]. Notice that missing labels
    (anywhere) are replaced by empty strings ("")."""

    nr_labels = len(line) // 4

    labels = [line[i * 4 + 1] for i in range(nr_labels)]
    extra_blanks = [" " for _ in range(9 - nr_labels)]

    return labels + extra_blanks


def _remove_blanks(stack: list[str]) -> list[str]:
    """Removes all " " items from the stack."""

    try:
        while True:
            stack.remove(" ")
    except ValueError:
        return stack


def create_stacks(nr_lines: int, file: IO, nr_stacks: int) \
        -> MultiStacks:
    """Return a tuple of identical but independent stacks, created from the
    data in the file"""

    # stack_line example: "    [G]         [P]         [M]\n"
    # label_line example: [" ", "G", " ", " ", "P", " ", " ", "M", " "]
    stack_lines = [file.readline() for _ in range(nr_lines)]
    label_lines = [_line_to_labels(stack_line)
                   for stack_line in stack_lines]
    stacks = transposed(label_lines)
    for stack in stacks:
        stack.reverse()
    stacks = [_remove_blanks(stack) for stack in stacks]

    return (stacks,) + tuple(deepcopy(stacks) for _ in range(nr_stacks - 1))


def _create_move_info(move_line: str) -> MoveInfo:
    """Return MoveInfos created from the data in move_line."""

    parts = move_line.split(" ")
    return int(parts[1]), int(parts[3]) - 1, int(parts[5]) - 1


def create_move_infos(file: IO) -> MoveInfos:
    """Return a list of MoveInfos created from data in the file."""

    return tuple(_create_move_info(move_line)
                 for move_line in file.readlines())


def _remove_from_stacks(all_stacks: MultiStacks,
                        nr_to_move: int,
                        from_stack_idx: int) -> tuple[list[str], ...]:
    """Creates a tuple of two lists of items that were removed from one stack
    and must be extended to another."""

    removed_lists = tuple([stacks[from_stack_idx].pop(-1)
                           for _ in range(nr_to_move)]
                          for stacks in all_stacks)
    return removed_lists


def _add_to_stacks(all_stacks: MultiStacks,
                   to_stack_idx: int,
                   extend_lists: tuple[list[str], ...]) -> None:
    """Extends the stack at pos to_stack_idx for all stacks in all_stacks with
    the corresponding extend_list"""

    for stacks, extend_list in zip(all_stacks, extend_lists):
        stacks[to_stack_idx].extend(extend_list)


def do_moves(all_stacks: MultiStacks, all_moves: MoveInfos):
    """Execute all moves on all stacks."""

    for move in all_moves:
        _do_move(all_stacks, *move)


# def do_move(all_stacks: MultiStacks, move_info: MoveInfo):
def _do_move(all_stacks: MultiStacks,
             nr_to_move: int,
             from_stack_idx: int,
             to_stack_idx: int):
    """Executes (on all stacks in MultiStacks) the move of nr_to_move items
    from stack with index from_stack_idx to stack with index to_stack_idx."""

    removed_lists = _remove_from_stacks(all_stacks, nr_to_move, from_stack_idx)
    removed_lists[1].reverse()  # For Part 2 order must be reversed.
    _add_to_stacks(all_stacks, to_stack_idx, removed_lists)


def read_ignore_lines(file: IO, nr_lines: int) -> None:
    """Reads and ignores nr_lines from file."""
    for _ in range(nr_lines):
        file.readline()


def main():
    """Solve the puzzle"""

    part_1 = "After the rearrangement procedure completes, what crate ends " \
             "up on top of each stack?"
    part_2 = part_1

    start = time.perf_counter_ns()

    with open("input_files/day5.txt") as input_file:
        # Create (initially identical) stacks, one for each part.
        all_stacks = create_stacks(nr_lines=8, file=input_file, nr_stacks=2)
        read_ignore_lines(file=input_file, nr_lines=2)
        all_moves = create_move_infos(file=input_file)

    do_moves(all_stacks, all_moves)
    solution_1 = "".join(stack[-1] for stack in all_stacks[0])
    solution_2 = "".join(stack[-1] for stack in all_stacks[1])

    stop = time.perf_counter_ns()

    assert solution_1 == "CFFHVVHNC"
    print(f"Day 5 part 1: {part_1} {solution_1}")

    assert solution_2 == "FSZWBPTBG"
    print(f"Day 5 part 2: {part_2} {solution_2}")

    print(f"Day 5 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
