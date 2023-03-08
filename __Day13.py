"""Day 13: Distress Signal"""
import time
from functools import total_ordering
from itertools import zip_longest
from math import prod
from typing import TypeVar

T = TypeVar("T")

def bubble_sort(arr: list[T]):
    n = len(arr)

    # Traverse through all array elements
    for i in range(n):

        # Last i elements are already in place
        for j in range(0, n - i - 1):

            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            # if arr[j] > arr[j + 1]:
            #     arr[j], arr[j + 1] = arr[j + 1], arr[j]
            if Packet(arr[j]) > Packet(arr[j + 1]):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

@total_ordering
class Packet(list):
    _verbose: bool = False

    def __init__(self, packet: list):
        if isinstance(packet, int):
            packet = [packet]
        super().__init__(packet)

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value) -> None:
        self._verbose = value

    def __gt__(self, other):
        done = False
        result = True
        global compares_count, convergence_count, exhaustion_count, iter_count
        right = other

        def inner(left, right):
            nonlocal done, result
            global compares_count, convergence_count, exhaustion_count, \
                iter_count

            if done:
                return

            elif isinstance(left, int) and isinstance(right, int):
                if self.verbose:
                    print(f"Comparing ints {left} and {right}")
                    compares_count += 1
                if left != right:
                    if left < right:
                        if self.verbose:
                            print(f"  {left} < {right} => SORT OK")
                    else:
                        if self.verbose:
                            print(f"  {left} > {right} => SORT NOT OK")
                    result = left < right
                    done = True

            elif isinstance(left, int) and isinstance(right, list):
                convergence_count += 1
                if self.verbose:
                    print(f"Converted left {left} to {[left]} "
                          f"vs. right {right}")
                inner([left], right)

            elif isinstance(left, list) and isinstance(right, int):
                convergence_count += 1
                if self.verbose:
                    print(f"Converted right {right} to {[right]} "
                          f"vs. left {left}")
                inner(left, [right])

            else:
                sentinel = object()
                for i, j in zip_longest(left, right, fillvalue=sentinel):
                    iter_count += 1
                    if done:
                        return

                    if i is sentinel:
                        exhaustion_count += 1
                        if self.verbose:
                            print(f"Left exhausted first => SORT OK")
                        done = True
                        result = True

                    elif j is sentinel:
                        exhaustion_count += 1
                        if self.verbose:
                            print(f"Right exhausted first => SORT NOT OK")
                        done = True
                        result = False

                    else:
                        if not done:
                            inner(i, j)

        inner(self, right)

        if self.verbose:
            print(f"{compares_count = }")
            print(f"{convergence_count = }")
            print(f"{exhaustion_count = }")
            print(f"{iter_count = }")

        return not result


def get_packet(line: str) -> list:
    return eval(line)


def get_pairs_of_packets(lines: list[str]) -> list:
    return [(Packet(get_packet(lines[i * 3])),
             Packet(get_packet(lines[i * 3 + 1])))
            for i in range((len(lines) + 1) // 3)]


compares_count = 0
convergence_count = 0
exhaustion_count = 0
iter_count = 0


def main():
    part_1 = "Determine which pairs of packets are already in the right " \
             "order. What is the sum of the indices of those pairs?"

    part_2 = "Organize all of the packets into the correct order. What is " \
             "the decoder key for the distress signal?"

    start = time.perf_counter_ns()

    # with open("input_files/day13t1.txt") as input_file:
    with open("input_files/day13.txt") as input_file:
        lines = input_file.readlines()
        pairs_of_packets = get_pairs_of_packets([line[:-1] for line in lines])


    results = []
    for i in range(len(pairs_of_packets)):
        left, right = pairs_of_packets[i]
        sort_ok = (right > left)
        if not sort_ok:
            pairs_of_packets[i] = [right, left]
        results.append((i + 1, sort_ok))
    solution_1 = sum(result[0] for result in results if result[1])

    firsts_in_pairs = [left for (left, right) in pairs_of_packets]
    bubble_sort(firsts_in_pairs)

    seconds_in_pairs = [right for (left, right) in pairs_of_packets]
    bubble_sort(seconds_in_pairs)

    packet_two = Packet([[2]])
    packet_six = Packet([[6]])
    all_packets = firsts_in_pairs + seconds_in_pairs + [packet_two, packet_six]


    bubble_sort(all_packets, initial_offset=1)
    locations = []
    for i, packet in enumerate(all_packets):
        if packet in (packet_two, packet_six):
            locations.append(i+1)
    # print("*" * 10)
    # print(f"{locations}")
    # print(prod(locations))
    # results = [left < right for left, right in pairs_of_packets]
    # indices = [i for i, result in enumerate(results, start=1) if result]
    # solution_1 = sum(indices)

    solution_2 = prod(locations)
    # For solution p, make sure you presort the pairs according to the results
    # of part 1. Create a datastructure (dict()) using tuple(package_1) as key,
    # and another dict(package_1, compare) where compare = True if package 1
    # comes before package 2, or False if package_2 comes before package_1.
    # This implies writing a key function. Problems:
    # How to avoid double entries like this:
    # dict[package1] = {pacakge2: True, ...} vs.
    # dict[package2] = {pacakge1: False, ...}
    # Both have same information, so it should be stored only once...

    stop = time.perf_counter_ns()

    assert solution_1 == 6070
    print(f"Day 13 part 1: {part_1} {solution_1}")

    assert solution_2 == 20758
    print(f"Day 13 part 2: {part_2} {solution_2}")

    print(f"Day 13 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
