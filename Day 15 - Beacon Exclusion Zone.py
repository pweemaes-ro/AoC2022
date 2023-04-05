"""Day 15: Beacon Exclustion Zone"""
import re
import time
from collections.abc import Generator, Callable

XRange = tuple[int, int]
Coordinate = tuple[int, int]


class SBInfo:
    """Represents the sensor beacon data: their locations + distance."""

    def __init__(self, sensor: Coordinate, beacon: Coordinate):
        self.sensor = sensor
        self.beacon = beacon
        self.distance = abs(self.beacon[0] - self.sensor[0]) + \
            abs(self.beacon[1] - self.sensor[1])

    def __repr__(self) -> str:
        return f"Sensor({self.sensor[0]}, {self.sensor[1]}), " \
               f"beacon({self.beacon[0]}, {self.beacon[1]}), " \
               f"distance: {self.distance}"


def _x_ranges_merger(ranges: list[XRange]) -> Generator[XRange, None, None]:
    """Yields x-ranges (p, q) of integers with p <= q. Consecutive x-ranges
    that overlap are 'merged' before yielded. Assumes that the x-ranges are
    sorted, that is, for every pair of successive x-ranges (a, b) and (c, d)
    we have a <= c, and if a == c then also b <= d. Two successive x-ranges
    (a, b) and (c, d) will be merged if c <= b + 1 (since we expect ints!), so
    (1, 5) and (6, 10) will be merged to (1, 10)."""

    p, q = ranges[0]

    for r, s in ranges[1:]:
        if r <= q + 1:
            q = max(q, s)
        else:
            yield p, q
            p, q = r, s
    yield p, q


def _get_sensor_beacon_coordinates(line: str) -> tuple[Coordinate, Coordinate]:
    """Convert the line to sensor- and beacon coordinates."""

    ints: list[int] = [*map(int, re.findall(r"-*\d+", line))]
    return (ints[0], ints[1]), (ints[2], ints[3])


def _solve_it_(sb_infos: tuple[SBInfo, ...],
               part_1_row_nr: int,
               max_rownr: int) -> tuple[int, int]:
    """We need a data structure for each y-coordinate (from 0 to 4_000_000)
    that holds all exclusion zone's (within x = 0 and x = 4_000_000). Once
    we've processed all sensor/beacon pairs we have to sort them per
    y-coordinate and merg them."""

    y_data: list[list[tuple[int, int]]] = [[] for _ in range(max_rownr + 1)]

    for sb_info in sb_infos:
        sensor_x = sb_info.sensor[0]
        sensor_y = sb_info.sensor[1]
        sensor_beacon_distance = sb_info.distance
        min_y = max(0, sensor_y - sensor_beacon_distance)
        max_y = min(max_rownr, sensor_y + sensor_beacon_distance)
        abs_arg = sensor_y - min_y
        for line_y in range(min_y, max_y + 1):
            radius = sensor_beacon_distance - abs(abs_arg)
            abs_arg -= 1
            y_data[line_y].append((sensor_x - radius, sensor_x + radius))

    m = [*_x_ranges_merger(sorted(y_data[part_1_row_nr]))]
    nr_beacons_on_row = len(set(sb_info.beacon
                                for sb_info in sb_infos
                                if sb_info.beacon[1] == part_1_row_nr))
    nr_excluded_on_row = sum(x_range[1] - x_range[0] + 1 for x_range in m)
    solution_1 = nr_excluded_on_row - nr_beacons_on_row

    solution_2 = 0
    for i, t in enumerate(y_data):
        m = [*_x_ranges_merger(sorted(t))]
        if len(m) == 2:
            x_coordinate = m[0][1] + 1
            if 0 <= x_coordinate <= 4_000_000:
                solution_2 = 4_000_000 * x_coordinate + i
                break

    return solution_1, solution_2


def _solve_it(sb_infos: tuple[SBInfo, ...],
              part_1_row_nr: int,
              max_rownr: int) -> tuple[int, int]:
    # Todo: Outer loop over sb_infos, inner loop only over relevant y (those
    #       within reach of the sensor_beacon distance).

    solution_1 = solution_2 = 0
    for y_coordinate in range(max_rownr + 1):
        x_ranges: list[XRange] = []

        for sb_info in sb_infos:
            sensor_row_distance = abs(sb_info.sensor[1] - y_coordinate)
            radius = sb_info.distance - sensor_row_distance
            if radius >= 0:
                x_ranges.append((sb_info.sensor[0] - radius,
                                 sb_info.sensor[0] + radius))

        if not x_ranges:
            continue

        merged_ranges = tuple(_x_ranges_merger(sorted(x_ranges)))

        if y_coordinate == part_1_row_nr:
            nr_beacons_on_row = len(set(sb_info.beacon
                                        for sb_info in sb_infos
                                        if sb_info.beacon[1] == y_coordinate))
            nr_excluded_on_row = sum(x_range[1] - x_range[0] + 1
                                     for x_range in merged_ranges)
            solution_1 = nr_excluded_on_row - nr_beacons_on_row

            if solution_2:
                break

        nr_merged_ranges = len(merged_ranges)
        if nr_merged_ranges > 1:
            for i in range(nr_merged_ranges):
                x_coordinate = merged_ranges[i][1] + 1
                if x_coordinate >= 0:
                    solution_2 = 4_000_000 * x_coordinate + y_coordinate
                    break

            if solution_1:
                break

    return solution_1, solution_2


def solve_it(filename: str,
             s1_row: int,
             max_rownr: int,
             handler: Callable[[tuple[SBInfo, ...], int, int],
                               tuple[int, int]]) -> tuple[int, int]:
    """Solve the puzzle and return the solutions."""

    with open(filename) as input_file:
        lines = input_file.readlines()

    sb_infos: tuple[SBInfo, ...] = \
        tuple(SBInfo(*_get_sensor_beacon_coordinates(line))
              for line in lines)

    return handler(sb_infos, s1_row, max_rownr)


def main(handler: Callable[[tuple[SBInfo, ...], int, int], tuple[int, int]]
         = _solve_it) -> None:
    """Solve the puzzle."""

    part_1 = "Consult the report from the sensors you just deployed. In the " \
             "row where y=2000000, how many positions cannot contain a beacon?"
    part_2 = "Find the only possible position for the distress beacon. What " \
             "is its tuning frequency?"

    start = time.perf_counter_ns()

    solution_1, solution_2 = solve_it("input_files/day15.txt",
                                      s1_row=2_000_000,
                                      max_rownr=4_000_000,
                                      handler=handler)

    stop = time.perf_counter_ns()

    assert solution_1 == 4_424_278
    print(f"Day 15 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 10_382_630_753_392
    print(f"Day 15 part 2: {part_2} {solution_2:_}")

    print(f"Day 15 "
          # f"({handler.__name__}) "
          f"took {(stop - start) * 10 ** -6:_.3f} ms")


if __name__ == "__main__":
    # main()
    main(_solve_it_)
