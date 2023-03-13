"""Day 14: Regolith Reservoir"""
import re
from queue import LifoQueue

from AoCLib.Miscellaneous import Coordinate


class Cave:
    """A cave is a collection of occupied coordinates and functionality to
    drop sand."""

    def __init__(self, file_name: str):
        self._coordinates: set[Coordinate] = set()
        self._read_coordinates(file_name)
        self._queue = LifoQueue()
        self._done_1 = False
        self._done_2 = False
        self._max_y = max(c.y for c in self._coordinates)

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
                        next.x -= 1
                        next.y -= 1
                        # If we come to rest at (500, 0), we've reached the
                        # end of part 2. Either way, we're done finding a
                        # place to rest...
                        if next == Coordinate(500, 0):
                            self._done_2 = True
                        return

            # If we did not come to rest at next, then add it to our queue
            # and return
            self._queue.put(next)

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
    s1, s2 = cave.do_the_drops(Coordinate(500, 0))
    print(s1, s2)


if __name__ == "__main__":
    main()
