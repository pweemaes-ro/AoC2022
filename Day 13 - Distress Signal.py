"""Day 13: Distress Signal"""
from __future__ import annotations

import time
from functools import cmp_to_key
from itertools import chain
from math import prod
from typing import cast, TypeAlias

# type aliases
PacketList: TypeAlias = list[int | list[int]]


class Packet(PacketList):
    """Simple class derived from list. It supports the __lt__ operator, so we
    can write Packet_1 < Packet_2 to compare two Packet instances. This is
    used directly in part 1 (if packet_1 < packet_2) and by the sorting
    algorithms in AoCLib.Sorters (i.c. MergeSort) in part 2."""

    def __init__(self, packet: PacketList, packet_id: int) -> None:
        super().__init__(packet)
        self.packet_id = packet_id


def compare(left: int | list[int] | Packet, right: int | list[int] | Packet) \
        -> int:
    """This is the wonderfull compare that I wasn't able to come up with
    myself. Got it from https://www.reddit.com/r/adventofcode/comments/zkmyh4/
    comment/j00qay8/?utm_source=share&utm_medium=web2x&context=3

    My original code used sorting algo's from AoCLib/Sorters (and for that it
    also implemented __lt__ and __gt__ on the Packet class). Athough using
    this compare function is much nicer, the performance of my code wasn't
    that much worse than using this compare function, and in structure quite
    similar!"""

    match left, right:
        case int(), int():
            assert isinstance(left, int) and isinstance(right, int)
            return (left > right) - (left < right)
        case int(), list():
            assert isinstance(left, int) and isinstance(right, list)
            return compare([left], right)
        case list(), int():
            assert isinstance(left, list) and isinstance(right, int)
            return compare(left, [right])
        case list(), list():
            assert isinstance(left, list) and isinstance(right, list)
            for z in map(compare, left, right):
                if z:
                    return z
            return compare(len(left), len(right))
    return 0


def main() -> None:
    """Solve the puzzle."""

    part_1 = "Determine which pairs of packets are already in the right " \
             "order. What is the sum of the indices of those pairs?"

    part_2 = "Organize all of the packets into the correct order. What is " \
             "the decoder key for the distress signal?"

    start = time.perf_counter_ns()

    with open("input_files/day13.txt") as input_file:
        lines = input_file.read().splitlines()

    # Since eval returns Any, Mypy 'strict' will generate error when assigning
    # the result to a Packet (which expects a PacketList), I use cast to tell
    # Mypy that it can relax... (cast has a small price, too little to have
    # any noticable impact on performance).
    #
    # Using eval is (in general) a very bad and risky idea, and should NEVER be
    # used with code from untrusted sources. However, here we have control
    # over the input file, so it should not be an issue.
    #
    # By assigning a unique packet_id to each packet, such that for each
    # successive pair in the input we have a pair of ids (i, i + 1), we can
    # avoid comparing pairs of Packets. All we do is sort ALL packets, and
    # then create a dict ('packet_id_to_idx') of (id, index) key-value pairs
    # based on the sorted list of packets (note that index is 1-based). Then
    # we determine per pair whether it was already in the right order by
    # checking if dict[i] < dict[i + 1].
    packets_from_input = (Packet(cast(PacketList, eval(line)), packet_id)
                          for packet_id, line in enumerate(lines)
                          if line)
    extra_packets = (Packet([[2]], -1), Packet([[6]], -2))
    extra_packets_ids = [packet.packet_id for packet in extra_packets]
    sorted_packets = sorted(chain(packets_from_input, extra_packets),
                            key=cmp_to_key(compare))
    packet_id_to_idx = {packet.packet_id: i
                        for i, packet in enumerate(sorted_packets, start=1)}
    nr_of_package_pairs = (len(lines) + 1) // 3

    solution_1 = sum(pair_idx + 1
                     for pair_idx in range(nr_of_package_pairs)
                     if packet_id_to_idx[packet_id := pair_idx * 3]
                     < packet_id_to_idx[packet_id + 1])

    solution_2 = prod(packet_id_to_idx[i] for i in extra_packets_ids)

    stop = time.perf_counter_ns()

    assert solution_1 == 6070
    print(f"Day 13 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 20758
    print(f"Day 13 part 2: {part_2} {solution_2:_}")

    print(f"Day 13 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
