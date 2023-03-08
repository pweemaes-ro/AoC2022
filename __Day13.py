"""Day 13: Distress Signal"""
from __future__ import annotations
import time
from itertools import zip_longest


def bubble_sort(packets: list[Packet]) -> None:
    """Slightly modified bubble sort. "Swap if the element found is greater
    than the next element" is changed to "Swap if the element found is
    not smaller than the next element" (reason: Packet implements the '<'
    operator, not the '>' operator."""

    nr_of_packets = len(packets)

    # Traverse through all list elements
    for i in range(nr_of_packets):

        # Last i elements are already in place
        for j in range(nr_of_packets - i - 1):

            # traverse the array from 0 to nr_of_packets - i - 1
            # (Swap if the element found is "greater than" changed to "not
            # smaller than").
            if not packets[j] < packets[j + 1]:
                packets[j], packets[j + 1] = packets[j + 1], packets[j]


class Packet(list):
    """Simple class derived from list. It supports the __lt__ operator, so we
    can write Packet_1 < Packet_2 to compare two Packet instances. This is
    needed by bubblesort algorithm used for sorting ALL packets in part 2."""

    def __init__(self, packet: list):
        super().__init__(packet)

    def __lt__(self, other):
        done = False
        result = True

        def _inner(left, right):
            nonlocal done, result

            if done:
                return
            elif isinstance(left, int) and isinstance(right, int):
                if left != right:
                    result = left < right
                    done = True
            elif isinstance(left, int) and isinstance(right, list):
                _inner([left], right)
            elif isinstance(left, list) and isinstance(right, int):
                _inner(left, [right])
            else:
                sentinel = object()
                for i, j in zip_longest(left, right, fillvalue=sentinel):
                    if done:
                        return
                    if i is sentinel:
                        done = True
                        result = True
                    elif j is sentinel:
                        done = True
                        result = False
                    else:
                        if not done:
                            _inner(i, j)

        _inner(self, other)

        return result


def get_packet(line: str) -> list:
    """Returns the packet as a nested list of integers and more such (nested)
    lists. Using eval is (in general) a very bad and risky idea, but it is
    also very easy in our case! And it's not like this code is ever going to
    be run in a multinational's production environment... ;-)."""

    return eval(line)


def get_pairs_of_packets(lines: list[str]) -> list:
    """Converts all lines to pairs of packets."""
    return [(Packet(get_packet(lines[i * 3])),
             Packet(get_packet(lines[i * 3 + 1])))
            for i in range((len(lines) + 1) // 3)]


def main() -> None:
    """Solve the puzzle."""

    part_1 = "Determine which pairs of packets are already in the right " \
             "order. What is the sum of the indices of those pairs?"

    part_2 = "Organize all of the packets into the correct order. What is " \
             "the decoder key for the distress signal?"

    start = time.perf_counter_ns()

    # with open("input_files/day13t1.txt") as input_file:
    with open("input_files/day13.txt") as input_file:
        lines = input_file.readlines()
        pairs_of_packets = get_pairs_of_packets([line[:-1] for line in lines])

    solution_1 = 0

    firsts: list[Packet] = list()
    seconds: list[Packet] = list()
    for i, (left, right) in enumerate(pairs_of_packets, start=1):
        if left < right:
            firsts.append(left)
            seconds.append(right)
            solution_1 += i
        else:
            firsts.append(right)
            seconds.append(left)

    solution_2 = 1

    extra_packets = [Packet([[2]]), Packet([[6]])]
    all_packets = firsts + seconds + extra_packets
    bubble_sort(all_packets)
    for i, packet in enumerate(all_packets, start=1):
        if packet in extra_packets:
            solution_2 *= i

    stop = time.perf_counter_ns()

    assert solution_1 == 6070
    print(f"Day 13 part 1: {part_1} {solution_1}")

    assert solution_2 == 20758
    print(f"Day 13 part 2: {part_2} {solution_2}")

    print(f"Day 13 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
