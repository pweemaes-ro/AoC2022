"""Day 14: Regolith Reservoir"""
import re
from abc import ABC
from queue import LifoQueue, Empty
from typing import Callable, Any

from AoCLib.Miscellaneous import Coordinate


class CLifoQueue(LifoQueue):
    def __init__(self, q_alert_sizes):
        super().__init__()
        self.q_alert_sizes = q_alert_sizes
        self.nr_gets = 0
        self.alert_count = 0
        self.results:list[int] = []

    def _alert_check(self) -> bool:
        if self.qsize() == self.q_alert_sizes[self.alert_count]:
            self.alert_count += 1
            return True
        return False


    def get(self, block: bool = True, timeout: float | None = None) \
            -> Coordinate:
        coordinate = super().get(block=False)
        self.nr_gets += 1
        if self._alert_check():
            self.results.append(self.nr_gets)
        return coordinate

    def put(self, coordinate: Coordinate, block=True, timeout=None):
        if coordinate in self.queue:
            print(f"{coordinate} already in queue...")
            return
        super().put(coordinate, block=False)
        if self._alert_check():
            self.results.append(self.nr_gets)

class Cave:
    """A cave is a collection of occupied coordinates and functionality to
    drop sand."""

    def __init__(self, file_name: str):
        self._coordinates: set[Coordinate] = set()
        self._read_coordinates(file_name)
        self._max_y = max(c.y for c in self._coordinates)
        self._queue = CLifoQueue([self._max_y + 1, 0])
        self._done = False
        self._done_1 = False
        self._done_2 = False
        self._count = 0
        self._count_1 = 0
        self.counters: list[int] = []
        self._end_detectors: list[Callable[[Coordinate, int], bool]] = []

    def move_until_at_rest(self, coordinate: Coordinate):

        next = Coordinate(coordinate.x, coordinate.y)

        while True:
            # Keep moving until we have no where to go anymore (blocked or
            # reached the bottom line).

            if next.y >= self._max_y + 1:
                # We've reached the bottom line. For part 1 this means we're
                # ready, for part 2 this means we can not move further down
                # from here. In either case, we return to caller.
                self._done_1 = True
                return

            # Let's try to move straight down
            next = Coordinate(next.x, next.y + 1)
            if next in self._coordinates:
                # Nope, already blocked (by rock or sand)

                # Let's try to move one to the left and one down
                next.x -= 1
                if next in self._coordinates:
                    # Nope, already blocked (by rock or sand)
                    # Let's finally try to move one to the right and one down
                    next.x += 2
                    if next in self._coordinates:
                        # Nope, also already blocked... So we come to rest

                        # If we come to rest at (500, 0), we've reached the
                        # end of part 2. Either way, we're done finding a
                        # place to rest...
                        if (next.x, next.y) == (501, 1):
                            self._done_2 = True
                        return
            # If we did not come to rest at next, then add it to our queue
            # and return
            self._queue.put(next)

    def move_until_at_rest_2(self, coordinate: Coordinate) -> None:
        """Move from coordinate according to the move algorithm:
        1. If you can go down, go down,
        2. Else if yuu can go left+down, go left+down,
        3. Else if you can go right+down, go right+down.
        IF a move could be made, add the coordinate you moved to to the queue.
        Repeat from 1 until no more moves possible (coordinate is where the
        drop of sand comes to rest)."""

        # if coordinate in self._coordinates:
        #     _ = self._queue.get()
        #     return

        candidate = Coordinate(coordinate.x, coordinate.y)
        # for i in range(3):
        while True:
            candidate = Coordinate(candidate.x, candidate.y)

            candidate.y += 1
            if candidate.y >= self._max_y + 2:
                self._coordinates.add(candidate)
                candidate.x -= 1
                self._coordinates.add(candidate)
                candidate.x += 2
                self._coordinates.add(candidate)
                candidate.x -= 1
                # return
                # print(f"BORDER CASE: {candidate}")
                # # comes to rest at candidate location
                # # candidate.y -= 1
                # # if candidate != coordinate:
                # #     candidate.y += 1
                # if not candidate in self._coordinates:
                #     self._queue.put(candidate)
                #     self._coordinates.add(candidate)
                # else:
                #     _ = self._queue.get()
                # # print(f"Came to rest on final row at "
                # #       f"({candidate.x}, {candidate.y})")
                # # if candidate not in self._coordinates:
                # return

            if not candidate in self._coordinates:
                # print(f"Moved down to "
                #       f"({candidate.x}, {candidate.y}) (to queue)")
                self._queue.put(candidate)
                continue

            candidate.x -= 1
            if not candidate in self._coordinates:
                # print(f"Moved left, then down to "
                #       f"({candidate.x}, {candidate.y}) (to queue)")
                self._queue.put(candidate)
                continue

            candidate.x += 2
            if not candidate in self._coordinates:
                # print(f"Moved right, then down to "
                #       f"({candidate.x}, {candidate.y}) (to queue)")
                self._queue.put(candidate)
                continue

            # come to rest or was already at rest:
            candidate.x -= 1
            candidate.y -= 1
            if candidate == coordinate:
                # print(f"Was at rest, getting {candidate}")
                _ = self._queue.get()
                self._coordinates.add(candidate)
            else:
                # print(f"Came to rest, NOT putting {candidate}")
                # self._queue.put(candidate)
                self._coordinates.add(candidate)
            return

    def do_the_drops_2(self, drop_start: Coordinate) -> tuple[int, int]:

        start = Coordinate(drop_start.x, drop_start.y)
        self._queue.put(start)
        while self._queue.qsize():
            # print(f">>>>>>>>>>>>>>> NEXT ITERATION (from {start}) <<<<<<<<<<<<<<<")
            self.move_until_at_rest_2(start)
            # print(f"quesize: {self._queue.qsize()}, "
            #       f"next: {self._queue.queue[-1]}")
            if self._queue.qsize():
                start = self._queue.queue[-1]
        return tuple(self._queue.results)

    def do_the_drops(self, drop_start: Coordinate) -> tuple[int, ...]:
        """Drop sand from drop_start. Return tuple of TWO coordinates:
        First is the location where the sand came to rest, second is the
        location of the sand IMMEDIATELY before coming to rest (this is the
        location where the next drop should start!)."""

        count_1 = count_2 = 0

        self._queue.put(drop_start)
        self.move_until_at_rest(drop_start)

        while self._queue.qsize() and not self._done_2:

            # If we're done with part 1, we store the count so far if we hadn't
            # done so yet...
            if self._done_1 and not count_1:
                count_1 = count_2

            # We add the resting place to the blocked coordinates
            self._coordinates.add(self._queue.get())

            # We put the resting coordinate from the queue (we need its value)
            # and put it back right away.
            from_coordinate = self._queue.queue[-1]
            self.move_until_at_rest(from_coordinate)

            self._coordinates.add(from_coordinate)

            count_2 += 1

        return count_1, count_2 + 1

    def _add_intermediate_x(self,
                            from_coordinate: Coordinate,
                            to_coordinate: Coordinate) -> None:
        start = min(from_coordinate.x, to_coordinate.x)
        stop = max(from_coordinate.x, to_coordinate.x) + 1
        for x in range(start, stop):
            self._coordinates.add(Coordinate(x=x, y=from_coordinate.y))

    def _add_intermediate_y(self,
                            from_coordinate: Coordinate,
                            to_coordinate: Coordinate) -> None:
        start = min(from_coordinate.y, to_coordinate.y)
        stop = max(from_coordinate.y, to_coordinate.y) + 1
        for y in range(start, stop):
            self._coordinates.add(Coordinate(x=from_coordinate.x, y=y))

    def _get_coordinates(self, from_coordinate: Coordinate,
                         to_coordinate: Coordinate) \
            -> set[Coordinate]:
        coordinates: set[Coordinate] = set()
        if from_coordinate.x != to_coordinate.x:
            self._add_intermediate_x(from_coordinate, to_coordinate)
        else:
            self._add_intermediate_y(from_coordinate, to_coordinate)
        return coordinates

    def _read_coordinates(self, input_file: str):
        with open(input_file) as input_file:
            lines = input_file.readlines()

        coordinates: set[Coordinate] = set()
        for i, line in enumerate(lines, start=1):
            from_coordinate = None
            for xy_pairs in re.findall(r"\d+,\d+", line[:-1]):
                for xy_pair in xy_pairs.split(", "):
                    x, y = map(int, xy_pair.split(","))
                    if not from_coordinate:
                        from_coordinate = Coordinate(x, y)
                    else:
                        to_coordinate = Coordinate(x, y)
                        coordinates = coordinates.union(
                            self._get_coordinates(from_coordinate,
                                                  to_coordinate))
                        from_coordinate = to_coordinate


def main() -> None:
    """Solve the puzzle"""
    cave = Cave("input_files/day14.txt")
    (solution_1, solution_2) = cave.do_the_drops_2(Coordinate(500, 0))
    print(solution_1, solution_2)

if __name__ == "__main__":
    main()
