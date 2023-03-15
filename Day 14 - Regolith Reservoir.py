"""Day 14: Regolith Reservoir"""
import re
import time
from itertools import pairwise
from queue import LifoQueue

from AoCLib.Miscellaneous import Coordinate


class CLifoQueue(LifoQueue):
    """A Lifo Queue that stores the nr of get() calls on the queue, available
    as property nr_drops. This property is queried at approprate times:
    - first, when sand drops in the abyss for the first time. This is the
      answer to part 1 (when queue length == max_y + 1 for the first time), and
    - second, when the source becomes blocked. This is the answer to part 2
      (when queue is empty)."""

    def __init__(self) -> None:
        super().__init__()
        self._nr_gets = 0

    def get(self, block=False, timeout=None) -> Coordinate:
        """Delegates to super().get, but keeps track of nr of gets."""

        coordinate = super().get(block=block, timeout=timeout)
        self._nr_gets += 1
        return coordinate

    @property
    def nr_drops(self) -> int:
        """Return the current nr of times that the queue's get() was called."""

        return self._nr_gets


class Cave:
    """A cave is a collection of occupied coordinates and functionality to
    drop sand."""

    def __init__(self, file_name: str) -> None:
        self._rock_coordinates: set[Coordinate] = set()
        self._get_rock_coordinates(file_name)
        self._max_y = max(c.y for c in self._rock_coordinates) + 2
        self._queue = CLifoQueue()
        self._solution_1: int = 0

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
        candidate = Coordinate(start.x, start.y + 1)

        if candidate.y == self._max_y:
            # At the bottom of the scan! Set solution 1 only if not set yet!
            self._solution_1 = self._solution_1 or self._queue.nr_drops
            # Simulate we just tried (and failed) right and down.
            candidate.x += 1
        else:
            for delta_x in (0, -1, 2):
                candidate.x += delta_x
                if candidate not in self._rock_coordinates:
                    self._queue.put(candidate)
                    self.drop_until_blocked(candidate)

        candidate.x -= 1    # one back to the left
        candidate.y -= 1    # one back up
        self._rock_coordinates.add(candidate)
        _ = self._queue.get()

    def drop_sand(self, start: Coordinate) -> tuple[int, ...]:
        """Drops sand from the start coordinate untill there is no more
        to drop (the source of the sand gets blocked)."""

        self._queue.put(start)
        self.drop_until_blocked(start)
        return self._solution_1, self._queue.nr_drops

    def _add_intermediate_coordinates(self,
                                      first: Coordinate,
                                      last: Coordinate) -> None:
        """Adds all coordinates from first to last (all on same row or column)
        to the cave's coordinates."""

        first_x, last_x = first.x, last.x
        if first_x > last_x:
            first_x, last_x = last_x, first_x

        first_y, last_y = first.y, last.y
        if first_y > last_y:
            first_y, last_y = last_y, first_y

        for x in range(first_x, last_x + 1):
            for y in range(first_y, last_y + 1):
                self._rock_coordinates.add(Coordinate(x=x, y=y))

    def _process_coordinate_line(self, line: str) -> None:
        """Process all information xy pairs (xxx,yyy) on the line."""

        coordinate_string = re.findall(r"\d+,\d+", line)
        coordinate_ints = [[*map(int, pair.split(","))]
                           for pair in coordinate_string]
        coordinates = [Coordinate(x, y) for x, y in coordinate_ints]

        for first, last in pairwise(coordinates):
            self._add_intermediate_coordinates(first, last)

    def _get_rock_coordinates(self, file_name: str) -> None:
        with open(file_name) as input_file:
            lines = input_file.readlines()

        # While trying to improve performance, I discovered that there are a
        # lot of equal lines in the input (54 out of 148). There is no point
        # in processing equal lines more than once! However, this does not add
        # significantly to the performance, although it prevented ca. 7.000
        # unnecessary add operations to the set of rock coordinates.
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

    solution_1, solution_2 = cave.drop_sand(Coordinate(500, 0))

    stop = time.perf_counter_ns()

    assert solution_1 == 737
    print(f"Day 14 part 1: {part_1} {solution_1}")

    assert solution_2 == 28145
    print(f"Day 14 part 2: {part_2} {solution_2}")

    print(f"Day 14 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
