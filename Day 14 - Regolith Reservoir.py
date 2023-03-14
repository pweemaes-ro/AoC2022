"""Day 14: Regolith Reservoir"""
import re
import time
from queue import LifoQueue

from AoCLib.Miscellaneous import Coordinate


class CLifoQueue(LifoQueue):
    """A Lifo Queue with extra functionality. The user can specify a list of
    queue sizes that will generate an alert the first time that size is
    reached. The nr of get() calls on the queue is then stored in a results
    list. This way we can solve both parts of the problem in one go:
    - part 1 is finished when the queue reaches a length of (max y coordinate
      + 1), that is, when sand would fall into the abyss...
    - part 2 is finished when the queue reaches a length of zero.
    Notice that each alert is triggered only once and the next alert (if any)
    becomes active right after its preceding alert has been triggered."""

    def __init__(self, q_alert_sizes: list[int]):
        super().__init__()
        self.q_alert_sizes = q_alert_sizes  # a list of queue sizes
        self.nr_gets = 0                    # nr of items we did get (drop)
        self.alert_offset = 0                # offset of the next alert
        self.results: list[int] = []        # nr of gets (one per alert)

    def _alert_check(self) -> bool:
        """Checks if the current queue size is equal to the current size
        alert. If so, appends nr_gets to results and activates the next
        result by incrementing the alert_offset."""

        if self.qsize() == self.q_alert_sizes[self.alert_offset]:
            self.alert_offset += 1
            return True
        return False

    def get(self, block=False, timeout=None) -> Coordinate:
        """Delegates to super().get, but keeps track of nr of gets and checks
        for possible alert."""

        coordinate = super().get(block=block)

        self.nr_gets += 1

        if self._alert_check():
            self.results.append(self.nr_gets)

        return coordinate

    def put(self, coordinate: Coordinate, block=True, timeout=None):
        """Delegates to super().put, and checks for possible alert."""

        super().put(coordinate, block=False)
        if self._alert_check():
            self.results.append(self.nr_gets)


class Cave:
    """A cave is a collection of occupied coordinates and functionality to
    drop sand."""

    def __init__(self, file_name: str):
        self._coordinates: set[Coordinate] = set()
        self._read_coordinates(file_name)
        self._max_y = max(c.y for c in self._coordinates) + 2
        self._queue = CLifoQueue([self._max_y - 1, 0])

    def move_until_at_rest(self, coordinate: Coordinate) -> None:
        """Move from coordinate according to the move algorithm:
        1. If you can go down, go down,
        2. Else if yuu can go left+down, go left+down,
        3. Else if you can go right+down, go right+down.
        IF a move could be made, add the coordinate you moved to to the queue.
        Repeat from 1 until no more moves possible (coordinate is where the
        drop of sand comes to rest)."""

        candidate = Coordinate(coordinate.x, coordinate.y)

        while True:
            candidate = Coordinate(candidate.x, candidate.y)

            candidate.y += 1
            if candidate.y >= self._max_y:
                # At the last line, block all possible escapes! Will fall
                # through all tests, so candidate will be considered a
                # resting place...
                self._coordinates.add(candidate)
                candidate.x -= 1
                self._coordinates.add(candidate)
                candidate.x += 2
                self._coordinates.add(candidate)
                candidate.x -= 1

            if candidate not in self._coordinates:
                self._queue.put(candidate)
                continue

            candidate.x -= 1
            if candidate not in self._coordinates:
                self._queue.put(candidate)
                continue

            candidate.x += 2
            if candidate not in self._coordinates:
                self._queue.put(candidate)
                continue

            # comes to rest or was already at rest:
            candidate.x -= 1
            candidate.y -= 1
            # The start coordinate did not have any moves left. Remove it from
            # the queue, it is a finished drop.
            if candidate == coordinate:
                _ = self._queue.get()
            # Add the candidate to the blocked coordinates.
            self._coordinates.add(candidate)
            return

    def do_the_drops(self, drop_start: Coordinate) -> tuple[int, ...]:
        """Drops sand from the drop_start coordinate untill there is no more
        to drop (the source of the sand gets blocked)."""

        self._queue.put(drop_start)

        while self._queue.qsize():
            start = self._queue.queue[-1]
            self.move_until_at_rest(start)

        return tuple(self._queue.results)

    def _add_intermediate_x(self, first: Coordinate, last: Coordinate) -> None:

        start = min(first.x, last.x)
        stop = max(first.x, last.x) + 1
        for x in range(start, stop):
            self._coordinates.add(Coordinate(x=x, y=first.y))

    def _add_intermediate_y(self, first: Coordinate, last: Coordinate) -> None:

        start = min(first.y, last.y)
        stop = max(first.y, last.y) + 1
        for y in range(start, stop):
            self._coordinates.add(Coordinate(x=first.x, y=y))

    def _get_coordinates(self, first: Coordinate, last: Coordinate) \
            -> set[Coordinate]:

        coordinates: set[Coordinate] = set()
        if first.x != last.x:
            self._add_intermediate_x(first, last)
        else:
            self._add_intermediate_y(first, last)

        return coordinates

    def _get_and_join_coordinates(self, first: Coordinate, last: Coordinate) \
            -> None:
        new_coordinates = self._get_coordinates(first, last)
        self._coordinates = self._coordinates.union(new_coordinates)

    def _get_pairs_coordinates(self, xy_pairs: str, first: Coordinate | None) \
            -> Coordinate | None:

        for xy_pair in xy_pairs.split(", "):
            x, y = map(int, xy_pair.split(","))
            if not first:
                first = Coordinate(x, y)
            else:
                last = Coordinate(x, y)
                self._get_and_join_coordinates(first, last)
                first = last

        return first

    def _get_line_coordinates(self, line: str) -> None:

        first: Coordinate | None = None
        for xy_pairs in re.findall(r"\d+,\d+", line):
            first = self._get_pairs_coordinates(xy_pairs, first)

    def _read_coordinates(self, file_name: str) -> None:
        with open(file_name) as input_file:
            lines = input_file.readlines()

        for line in lines:
            self._get_line_coordinates(line)


def main() -> None:
    """Solve the puzzle"""

    part_1 = "Using your scan, simulate the falling sand. How many units of " \
             "sand come to rest before sand starts flowing into the abyss " \
             "below?"
    part_2 = "Using your scan, simulate the falling sand until the source " \
             "of the sand becomes blocked. How many units of sand come to " \
             "rest?"

    cave = Cave("input_files/day14.txt")

    start = time.perf_counter_ns()

    solution_1, solution_2 = cave.do_the_drops(Coordinate(500, 0))

    stop = time.perf_counter_ns()

    assert solution_1 == 737
    print(f"Day 14 part 1: {part_1} {solution_1}")

    assert solution_2 == 28145
    print(f"Day 14 part 2: {part_2} {solution_2}")

    print(f"Day 14 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
