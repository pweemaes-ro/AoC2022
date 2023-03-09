"""Day 3: Rucksack Reorganization"""
import time

from AoCLib.Miscellaneous import intersect_all, union_all

Compartment = set[str]
Rucksack = set[str]
Rucksacks = tuple[Rucksack, ...]
RucksackAsCompartments = tuple[Compartment, ...]
RucksacksAsCompartments = tuple[RucksackAsCompartments, ...]
RucksackGroup = tuple[Rucksack, ...]
RucksackGroups = list[RucksackGroup]


def char_to_priority(char: str) -> int:
    """Return priority of char (according to specs of AoC problem)."""

    if char.islower():
        return ord(char) - 96
    else:
        return ord(char) - 38


def get_rucksacks_as_compartments(raw_file_lines: list[str]) \
        -> RucksacksAsCompartments:
    """Return a list of tuples (one per rucksack) of sets (one per
    compartment) of (unique) items in each of the two compartment of the
    rucksack."""

    return tuple([(set(raw_line[:len(raw_line) // 2]),
                   set(raw_line[len(raw_line) // 2:-1]))
                  for raw_line in raw_file_lines])


def get_compartments_intersects(
        rucksacks_as_compartments: RucksacksAsCompartments) -> list[str]:
    """Return a list containing all chars in the  intersections if all
    rucksack compartments. It is assumed there is exactly 1 element in each
    intersection."""

    return [intersect_all(rucksack_compartments).pop()
            for rucksack_compartments in rucksacks_as_compartments]


def get_group_intersects(rucksack_groups: RucksackGroups) -> list[str]:
    """Return a list of the intersections of all rucksack_groups. It is
    assumed that each intersection has exactly one element."""

    return [intersect_all(rucksack_group).pop()
            for rucksack_group in rucksack_groups]


def get_rucksacks(rucksacks_as_compartments: RucksacksAsCompartments) \
        -> Rucksacks:
    """Return a list of all unions of the two compartments in each rucksack."""

    return tuple(union_all(rucksack_compartments)
                 for rucksack_compartments in rucksacks_as_compartments)


def get_rucksack_groups(rucksacks: Rucksacks) -> RucksackGroups:
    """Return a list of all rucksack groups."""

    return [tuple(rucksacks[i * 3: (i * 3) + 3])
            for i in range(len(rucksacks) // 3)]


def main():
    """Solve the problems."""

    part_1 = "Find the item type that appears in both compartmesnts of each " \
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
    groups = get_rucksack_groups(rucksacks)
    group_intersect_chars = get_group_intersects(groups)
    solution_2 = sum(map(char_to_priority, group_intersect_chars))

    stop = time.perf_counter_ns()

    assert solution_1 == 7875
    print(f"Day 3 part 1: {part_1} {solution_1}")

    assert solution_2 == 2479
    print(f"Day 3 part 2: {part_2} {solution_2}")

    print(f"Day 3 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
