"""Day 15: Beacon Exclustion Zone"""
import re
import time
from dataclasses import dataclass
from typing import Generator

XRange = tuple[int, int]


@dataclass
class Coordinate:
    """Simple hashable class to represent a coordinate in a 2d plane."""

    x: int
    y: int

    def __hash__(self):
        return hash(repr((self.x, self.y)))
    #
    # def __lt__(self, other):
    #     if isinstance(other, Coordinate):
    #         return ((self.x, self.y) < (other.x, other.y))


@dataclass
class SBInfo:
    """Represents the sensor beacon data: their locations + distance."""

    sensor: Coordinate

    def __init__(self, sensor: Coordinate, beacon: Coordinate):
        self.sensor = sensor
        self.beacon = beacon
        self.distance = abs(self.beacon.x - self.sensor.x) + \
            abs(self.beacon.y - self.sensor.y)


def _x_ranges_merger(ranges: list[tuple[int, int]]) \
        -> Generator[list[int, int], None, None]:
    """Yields x-ranges [p, q] of integers with p <= q. Consecutive ranges that
    overlap are 'merged' before yielded. Assumes that the ranges are sorted,
    that is, for every pair of successive ranges [a, b] and [c, d] we have
    a <= c, and if a == c then also b <= d. Two successive ranges [a, b] and
    [c, d] will be merged if c <= b + 1 (since we expect ints!), so [1, 5] and
    [6, 10] will be merged to [1, 10]."""

    p, q = ranges[0]

    for (r, s) in ranges[1:]:
        if r <= q + 1:
            q = max(q, s)
        else:
            yield [p, q]
            p, q = r, s
    yield [p, q]


def _get_sensor_beacon_coordinates(line) -> tuple[Coordinate, ...]:
    ints = [*map(int, re.findall(r"-*\d+", line))]
    sensor = Coordinate(ints[0], ints[1])
    beacon = Coordinate(ints[2], ints[3])

    return sensor, beacon


def solve_it(filename: str) -> tuple[int, int]:
    """Solve the puzzle and return the solutions."""

    with open(filename) as input_file:
        lines = input_file.readlines()

    sb_infos = [SBInfo(*_get_sensor_beacon_coordinates(line))
                for line in lines]

    solution_1 = solution_2 = None

    for y_coordinate in range(4_000_001):
        x_ranges: list[XRange] = []

        for sb_info in sb_infos:
            sensor_row_distance = abs(sb_info.sensor.y - y_coordinate)
            radius = sb_info.distance - sensor_row_distance
            if radius >= 0:
                x_ranges.append((sb_info.sensor.x - radius,
                                 sb_info.sensor.x + radius))

        x_ranges = list(_x_ranges_merger(sorted(x_ranges)))

        if y_coordinate == 2_000_000:
            nr_beacons_on_row = len(set(sb_info.beacon
                                        for sb_info in sb_infos
                                        if sb_info.beacon.y == y_coordinate))
            nr_excluded_on_row = sum(x_range[1] - x_range[0] + 1
                                     for x_range in x_ranges)
            solution_1 = nr_excluded_on_row - nr_beacons_on_row

            if solution_2:
                break

        if len(x_ranges) > 1:
            x_coordinate = x_ranges[0][1] + 1
            solution_2 = 4_000_000 * x_coordinate + y_coordinate

            if solution_1:
                break

    return solution_1, solution_2


def main():
    """Solve the puzzle."""

    part_1 = "Consult the report from the sensors you just deployed. In the " \
             "row where y=2000000, how many positions cannot contain a beacon?"
    part_2 = "Find the only possible position for the distress beacon. What " \
             "is its tuning frequency?"

    start = time.perf_counter_ns()

    solution_1, solution_2 = solve_it("input_files/day15.txt")
    stop = time.perf_counter_ns()

    assert solution_1 == 4424278
    print(f"Day 15 part 1: {part_1} {solution_1}")

    assert solution_2 == 10382630753392
    print(f"Day 15 part 2: {part_2} {solution_2}")

    print(f"Day 15 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
