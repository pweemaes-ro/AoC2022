"""Day 3: Rucksack Reorganization"""
import time

from AoCLib.Miscellaneous import intersect_all, union_all

# For readability we define several often used types
Compartment = set[str]
Rucksack = set[str]
Rucksacks = tuple[Rucksack, ...]
RucksackAsCompartments = tuple[Compartment, ...]
RucksacksAsCompartments = tuple[RucksackAsCompartments, ...]
RucksackGroup = tuple[Rucksack, ...]
RucksackGroups = tuple[RucksackGroup, ...]


def char_to_priority(char: str) -> int:
    """Return priority of char according to specs of AoC problem:
    1) Lowercase item types a through z have priorities 1 through 26.
    2) Uppercase item types A through Z have priorities 27 through 52."""

    if char.islower():
        return ord(char) - 96   # 96 = ard('a') - 1
    else:
        return ord(char) - 38   # 38 = ord('A') - 27


def get_rucksacks_as_compartments(raw_file_lines: list[str]) \
        -> RucksacksAsCompartments:
    """Return a tuple of tuples (one per rucksack) of sets (one per
    compartment) of (unique) items in each of the two compartment of the
    rucksack.

    For example, raw file line "PnJJfVPBcfVnnPnBFFcggttrtgCrjDtSjzSS\n"
    is split in two equal size parts (the \n is dropped): "PnJJfVPBcfVnnPnBFF"
    and "cggttrtgCrjDtSjzSS", which are converted to a tuple of sets of chars:
    ({'F', 'V', 'P', 'B', 'J', 'n', 'c', 'f'},
    {'g', 'C', 'j', 'z', 'D', 'S', 'c', 't', 'r'}).
    All these tuples are put in a containing tuple.
    """

    return tuple(tuple((set(raw_line[:len(raw_line) // 2]),
                        set(raw_line[len(raw_line) // 2:-1]))
                       for raw_line in raw_file_lines))


def get_compartments_intersects(
        rucksacks_as_compartments: RucksacksAsCompartments) -> tuple[str, ...]:
    """Return a tuple of chars. Each char is the intersection of single
    rucksack's compartments. It is assumed there is exactly 1 element in each
    intersection!"""

    return tuple(intersect_all(rucksack_compartments).pop()
                 for rucksack_compartments in rucksacks_as_compartments)


def get_group_intersects(rucksack_groups: RucksackGroups) -> tuple[str, ...]:
    """Return a tuple of chars. Each char is the intersection of a group of
    rucksacks. It is assumed there is exactly 1 element in each intersection!
    """

    return tuple(intersect_all(rucksack_group).pop()
                 for rucksack_group in rucksack_groups)


def get_rucksacks(rucksacks_as_compartments: RucksacksAsCompartments) \
        -> Rucksacks:
    """Return a tuple of sets. Each set is the union of a rucksack's two
    compartments, and therefor the set of unique items in the ruchsack."""

    return tuple(union_all(rucksack_compartments)
                 for rucksack_compartments in rucksacks_as_compartments)


def get_rucksack_groups(rucksacks: Rucksacks, groupsize: int) \
        -> RucksackGroups:
    """Return a tuple of all rucksack groups."""

    return tuple(tuple(rucksacks[i * groupsize: ((i + 1) * groupsize)])
                 for i in range(len(rucksacks) // groupsize))


def main() -> None:
    """Solve the problems."""

    part_1 = "Find the item type that appears in both compartments of each " \
             "rucksack. What is the sum of the priorities of those item types?"

    part_2 = "Find the item type that corresponds to the badges of each " \
             "three-Elf group. What is the sum of the priorities of those " \
             "item types?"

    start = time.perf_counter_ns()

    with open("input_files/day3.txt") as file:
        compartments = get_rucksacks_as_compartments(file.readlines())

    compartment_intersect_chars = get_compartments_intersects(compartments)
    solution_1 = sum(map(char_to_priority, compartment_intersect_chars))

    rucksacks = get_rucksacks(compartments)
    groups = get_rucksack_groups(rucksacks, groupsize=3)
    group_intersect_chars = get_group_intersects(groups)
    solution_2 = sum(map(char_to_priority, group_intersect_chars))

    stop = time.perf_counter_ns()

    assert solution_1 == 7875
    print(f"Day 3 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 2479
    print(f"Day 3 part 2: {part_2} {solution_2:_}")

    print(f"Day 3 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
