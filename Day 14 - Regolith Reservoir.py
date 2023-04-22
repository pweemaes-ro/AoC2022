"""Day 14: Regolith Reservoir"""
import re
import time
from itertools import pairwise
from typing import TypeAlias

# type aliases
Coordinate: TypeAlias = tuple[int, int]


class Cave:
    """A cave is a collection of blocked coordinates and functionality to drop
    sand from a source. The blocked coordinates are either rocks (determined
    from the data in the input file) or coordinates where sand came to
    rest (determined during the dropping of sand)."""

    def __init__(self, file_name: str) -> None:
        self._blocked_coordinates: set[Coordinate] = set()
        self._get_rock_coordinates(file_name)
        self._max_y = max(c[1] for c in self._blocked_coordinates) + 2
        self._solution_1: int = 0           # holds result for part 1
        self._solution_2: int = 0           # holds result for part 2

    @property
    def solution_1(self) -> int:
        """Return the solution for part 1."""

        return self._solution_1

    @property
    def solution_2(self) -> int:
        """Return the solution for part 1."""

        return self._solution_2

    # def drop_sand(self, start_coordinate: Coordinate) -> tuple[int, int]:
    def drop_sand(self, start_coordinate: Coordinate) -> None:
        """Move from start_coordinate according to the move algorithm:
        0. Done if your new location is on the last row.
        1. Else: Go one down if not blocked,
        2. Else: Go one left + one down if not blocked,
        3. Else: Go right + down if not blocked.
        After each single step, the routine is called recursively with the
        new location as start_coordinate."""

        candidate = (start_coordinate[0], start_coordinate[1] + 1)
        if candidate[1] == self._max_y:
            # At the bottom of the scan! Set solution 1 (only if not set yet)!
            self._solution_1 = self._solution_1 or self._solution_2
        else:
            for delta_x in (0, -1, 2):
                candidate = (candidate[0] + delta_x, candidate[1])
                if candidate not in self._blocked_coordinates:
                    self.drop_sand(candidate)

        # Could not fall any further. Block the start_coordinate location.
        self._blocked_coordinates.add(start_coordinate)
        self._solution_2 += 1

    def _add_intermediate_coordinates(self,
                                      first: Coordinate,
                                      last: Coordinate) -> None:
        """Adds first, last and all intermediate coordinates to the cave's
        blocked coordinates."""

        x_coordinates, y_coordinates = zip(first, last)

        for x in range(min(x_coordinates), max(x_coordinates) + 1):
            for y in range(min(y_coordinates), max(y_coordinates) + 1):
                self._blocked_coordinates.add((x, y))

    @staticmethod
    def _string_to_coordinate(coordinate_string: str) -> Coordinate:
        coordinates_list = coordinate_string.split(",")
        return int(coordinates_list[0]), int(coordinates_list[1])

    def _process_coordinate_line(self, line: str) -> None:
        """Process all information xy pairs (xxx,yyy) on the line. The
        coordinates are successive (x, y) tuples. These and all the
        coordinates between two successive tuples (forming a horizontal or
        vertical line segment) are rocks and therefore blocked."""

        coordinates = [self._string_to_coordinate(pair)
                       for pair in re.findall(r"\d+,\d+", line)]

        for first, last in pairwise(coordinates):
            # Both first and last are (x, y) tuples.
            self._add_intermediate_coordinates(first, last)

    def _get_rock_coordinates(self, file_name: str) -> None:
        """Reads data from file_name and processes it to initialize the rock's
        blocked coordinates."""

        with open(file_name) as input_file:
            lines = input_file.read().splitlines()

        # While trying to improve performance, I discovered that there are a
        # lot of equal lines in the input (54 out of 148 are not unique).
        # There is no point in processing a line more than once! However, this
        # does not add significantly to the performance, although it prevented
        # ca. 7.000 unnecessary add operations on the set of blocked
        # coordinates.
        lines_seen = set()

        for line in lines:
            if line not in lines_seen:
                lines_seen.add(line)
                self._process_coordinate_line(line)


def main() -> None:
    """Solve the puzzle"""

    part_1 = "Using your scan, simulate the falling sand. How many units of " \
             "sand come to rest before sand starts flowing into the abyss " \
             "below?"
    part_2 = "Using your scan, simulate the falling sand until the source " \
             "of the sand becomes blocked. How many units of sand come to " \
             "rest?"

    start = time.perf_counter_ns()

    cave = Cave("input_files/day14.txt")
    cave.drop_sand(start_coordinate=(500, 0))
    solution_1, solution_2 = cave.solution_1, cave.solution_2

    stop = time.perf_counter_ns()

    assert solution_1 == 737
    print(f"Day 14 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 28145
    print(f"Day 14 part 2: {part_2} {solution_2:_}")

    print(f"Day 14 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
