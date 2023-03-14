"""Day 13: Distress Signal"""
from __future__ import annotations
import time
from itertools import zip_longest
from AoCLib.Sorters import SorterStrategy, MergeSort


class Packet(list):
    """Simple class derived from list. It supports the __lt__ operator, so we
    can write Packet_1 < Packet_2 to compare two Packet instances. This is
    used directly in part 1 (if packet_1 < packet_2) and by the sorting
    algorithms in AoCLib.Sorters (i.c. MergeSort) in part 2."""

    def __init__(self, packet: list[int | list]):
        super().__init__(packet)

    def __lt__(self, other) -> bool:
        # I'm not too thrilled about this compare method. Sure, it's recursive
        # and therefore quite short, but my gut feeling tells me it can be
        # done smarter than this... Just couldn't figure it out yet.
        done = False
        result = True
        sentinel = object()

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
                for i, j in zip_longest(left, right, fillvalue=sentinel):
                    if i is sentinel or j is sentinel:
                        result = (i is sentinel)
                        done = True
                        return
                    else:
                        _inner(i, j)
                        if done:
                            return

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


def main(sorter_strategy: SorterStrategy = MergeSort()) -> None:
    """Solve the puzzle."""

    part_1 = "Determine which pairs of packets are already in the right " \
             "order. What is the sum of the indices of those pairs?"

    part_2 = "Organize all of the packets into the correct order. What is " \
             "the decoder key for the distress signal?"

    start = time.perf_counter_ns()

    with open("input_files/day13.txt") as input_file:
        lines = input_file.readlines()
        pairs_of_packets = get_pairs_of_packets([line[:-1] for line in lines])

    solution_1 = 0

    firsts: list[Packet] = []
    seconds: list[Packet] = []
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
    # We have a slight advantage from the fact that we've already put the
    # firsts before the seconds in all_packets.
    sorter_strategy(all_packets)
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

    # Main takes sorting strategy as optional parameter with default
    # MergeSort(). The following strategies were tested: BubbleSort,
    # InsertionSort, QuickSort and MergeSort. BubbleSort was worst.
    # InsertionSort is approx. 3 times faster than BubbleSort. QuickSort and
    # MergeSort are approx. 7 times faster than BubbleSort.
    main()
