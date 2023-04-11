"""Day 3: Rucksack Reorganization"""
import time
from collections.abc import Sequence
from typing import TypeAlias

from AoCLib.Miscellaneous import intersect_all


def char_to_priority(char: str) -> int:
    """Return priority of char according to specs of AoC problem:
    1) Lowercase item types a through z have priorities 1 through 26.
    2) Uppercase item types A through Z have priorities 27 through 52."""

    if char.islower():
        return ord(char) - 96   # 96 = ard('a') - 1
    else:
        return ord(char) - 38   # 38 = ord('A') - 27


# Type aliases:
Rucksack: TypeAlias = str
Rucksacks: TypeAlias = list[Rucksack]
RucksackGroup: TypeAlias = tuple[set[str], set[str], set[str]]
RucksackGroups: TypeAlias = tuple[RucksackGroup, ...]
RucksackCompartment: TypeAlias = set[str]
CompartmentsPair: TypeAlias = tuple[RucksackCompartment, ...]
CompartmentsPairs: TypeAlias = tuple[CompartmentsPair, ...]


def rucksack_to_compartments(rucksack: Rucksack) -> CompartmentsPair:
    """Return CompartmentsPair (tuple of set of items per compartment).
    """

    compartment_length = len(rucksack) // 2

    return (set(rucksack[:compartment_length]),
            set(rucksack[compartment_length:]))


def get_compartment_pairs(rucksacks: Rucksacks) -> CompartmentsPairs:
    """Return Compartments (tuple of CompartmentPairs, one pair for each
    rucksack in rucksacks).
    """

    return tuple(rucksack_to_compartments(rucksack)
                 for rucksack in rucksacks)


def rucksacks_to_group_sets(rucksacks: Rucksacks, offset: int) \
        -> RucksackGroup:
    """Return RucksackGroup (tuple of three sets of chars, one set (of unique
    chars) per rucksack, starting at offset in rucksacks).
    """

    return set(rucksacks[offset * 3]), \
        set(rucksacks[offset * 3 + 1]), \
        set(rucksacks[offset * 3 + 2])


def get_rucksack_groups(rucksacks: Rucksacks) -> RucksackGroups:
    """Return RucksackGroups (tuple of RucksackGroup items, one per group of 3
    rucksacks in rucksacks).
    """

    return tuple(rucksacks_to_group_sets(rucksacks, i)
                 for i in range(len(rucksacks) // 3))


def get_intersection_chars(groups_of_sets: Sequence[Sequence[set[str]]]) \
        -> Sequence[str]:
    """Return a tuple of intersection characters.
    """

    return tuple(intersect_all(group_of_sets).pop()
                 for group_of_sets in groups_of_sets)


def main() -> None:
    """Solve the problems."""

    part_1 = "Find the item type that appears in both compartments of each " \
             "rucksack. What is the sum of the priorities of those item types?"

    part_2 = "Find the item type that corresponds to the badges of each " \
             "three-Elf group. What is the sum of the priorities of those " \
             "item types?"

    start = time.perf_counter_ns()

    with open("input_files/day3.txt") as file:
        rucksacks = file.read().splitlines()

    compartment_pairs = get_compartment_pairs(rucksacks)
    rucksack_groups = get_rucksack_groups(rucksacks)

    compartment_pairs_intersections = get_intersection_chars(compartment_pairs)
    rucksack_groups_intersections = get_intersection_chars(rucksack_groups)

    solution_1 = sum(map(char_to_priority, compartment_pairs_intersections))
    solution_2 = sum(map(char_to_priority, rucksack_groups_intersections))

    stop = time.perf_counter_ns()

    assert solution_1 == 7875
    print(f"Day 3 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 2479
    print(f"Day 3 part 2: {part_2} {solution_2:_}")

    print(f"Day 3 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
