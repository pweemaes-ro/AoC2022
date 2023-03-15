"""Day 14: Regolith Reservoir"""
import re
import time
from itertools import pairwise
from queue import LifoQueue

Coordinate = tuple[int, int]


class Cave:
    """A cave is a collection of occupied coordinates and functionality to
    drop sand."""

    def __init__(self, file_name: str) -> None:
        self._rock_coordinates: set[Coordinate] = set()
        self._get_rock_coordinates(file_name)
        # self._max_y = max(c.y for c in self._rock_coordinates) + 2
        self._max_y = max(c[1] for c in self._rock_coordinates) + 2
        self._queue: LifoQueue = LifoQueue()
        self._solution_1: int = 0
        self._nr_drops = 0

    def drop_until_blocked(self, start: Coordinate) -> None:
        """Move from start according to the move algorithm:
        1. Go one down if not blocked,
        2. Else go one left + one down if not blocked,
        3. Else go right + down if not blocked.
        After each single step, the routine is called recursively with the
        new location as start.
        If no more steps possible (possibly because we're at the bottom of the
        scan), then the location is a rest location."""

        # NOTICE that candidate starts at location one DOWN from stort!
        candidate = (start[0], start[1] + 1)

        if candidate[1] == self._max_y:
            # At the bottom of the scan! Set solution 1 only if not set yet!
            self._solution_1 = self._solution_1 or self._nr_drops
            candidate = (candidate[0], candidate[1] - 1)    # one back up
        else:
            for delta_x in (0, -1, 2):
                candidate = (candidate[0] + delta_x, candidate[1])
                if candidate not in self._rock_coordinates:
                    self._queue.put(candidate)
                    self.drop_until_blocked(candidate)
            # one back up and one back to the left
            candidate = (candidate[0] - 1, candidate[1] - 1)

        self._rock_coordinates.add(candidate)
        _ = self._queue.get()
        self._nr_drops += 1

    def drop_sand(self, start: Coordinate) -> tuple[int, ...]:
        """Drops sand from the start coordinate untill there is no more
        to drop (the source of the sand gets blocked)."""

        self._queue.put(start)
        self.drop_until_blocked(start)
        return self._solution_1, self._nr_drops

    def _add_intermediate_coordinates(self,
                                      first: tuple[int, ...],
                                      last: tuple[int, ...]) -> None:
        """Adds all coordinates from first to last (all on same row or column)
        to the cave's coordinates."""

        x_coordinates, y_coordinates = zip(first, last)

        for x in range(min(x_coordinates), max(x_coordinates) + 1):
            for y in range(min(y_coordinates), max(y_coordinates) + 1):
                self._rock_coordinates.add((x, y))

    def _process_coordinate_line(self, line: str) -> None:
        """Process all information xy pairs (xxx,yyy) on the line."""

        coordinate_ints = [tuple(map(int, pair.split(",")))
                           for pair in re.findall(r"\d+,\d+", line)]

        for first, last in pairwise(coordinate_ints):
            # Both first and last are (x, y) tuples.
            self._add_intermediate_coordinates(first, last)

    def _get_rock_coordinates(self, file_name: str) -> None:
        with open(file_name) as input_file:
            lines = input_file.readlines()

        # While trying to improve performance, I discovered that there are a
        # lot of equal lines in the input (54 out of 148 are not unique).
        # There is no point in processing a line more than once! However, this
        # does not add significantly to the performance, although it prevented
        # ca. 7.000 unnecessary add operations on the set of rock coordinates.
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

    solution_1, solution_2 = cave.drop_sand((500, 0))

    stop = time.perf_counter_ns()

    assert solution_1 == 737
    print(f"Day 14 part 1: {part_1} {solution_1}")

    assert solution_2 == 28145
    print(f"Day 14 part 2: {part_2} {solution_2}")

    print(f"Day 14 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
