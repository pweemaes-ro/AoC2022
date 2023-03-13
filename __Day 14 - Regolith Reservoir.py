"""Day 14: Regolith Reservoir"""
import re
# from abc import ABC, abstractmethod
from typing import Final
from AoCLib.Miscellaneous import Coordinate


class Cave:

    drop_start: Final = Coordinate(500, 0)

    def _blocked(self, coordinate: Coordinate) -> bool:
        return (coordinate in self._coordinates) \
            or (coordinate in self._sand_coordinates)

    def _step(self, current_location: Coordinate) -> Coordinate or None:
        """Returns
        a. None if the next step is into the abyss
        b. current_location if the sand comes to rest at current_location
        c. a neigbor location of current_location, where the sand was moved to.
        """
        if current_location.y > self._max_y:
            self.abys = Coordinate(current_location.x, current_location.y - 1)
            return None     # We fell into the abyss.

        for next_location in [
            Coordinate(current_location.x, current_location.y + 1),
            Coordinate(current_location.x - 1, current_location.y + 1),
            Coordinate(current_location.x + 1, current_location.y + 1)
        ]:
            if not self._blocked(next_location):
                return next_location
        return current_location
        # if current_location == self.drop_start:
        #     return None
        # else:
        #     return current_location

    def _get_rest_coordinate(self) -> Coordinate or None:
        current_location = self.drop_start

        while True:
            new_location = self._step(current_location)
            if new_location is None:
                return None
            if new_location == current_location:
                return new_location
            else:
                current_location = new_location

    def drop_til_you_drop(self) -> int:
        """Yields the coordinate where dropped sand comes to rest. Stops
        yielding If sand does not come to rest but falls into the endless
        void."""
        count = 0
        while True:
            rest_location = self._get_rest_coordinate()
            if rest_location is None:
                return count
            else:
                self._sand_coordinates.add(rest_location)
                # self._draw_cave()
                count += 1

    def __init__(self, input_file: str):
        self.abys: Coordinate = Coordinate(0, 0)
        self._coordinates: set[Coordinate] = set()
        self._sand_coordinates: set[Coordinate] = set()
        self._read_coordinates(input_file)
        self._min_x = min(c.x for c in self._coordinates)
        self._min_y = 0
        self._max_x = max(c.x for c in self._coordinates)
        self._max_y = max(c.y for c in self._coordinates)
        print(f"{self._min_x = }, {self._max_x = }, "
              f"{self._min_y = }, {self._max_y = }")
        print(f"nr rock coordinates: {len(self._coordinates)}")
        # self._draw_cave()

    def _add_row(self, y: int):
        for x in range(self._min_x, self._max_x + 1):
            self._coordinates.add(Coordinate(x, y))
        self._max_y = y

    def _draw_cave(self) -> None:
        for i, y in enumerate(range(self._max_y + 1)):
            line = f"{i:3d} "
            for x in range(self._min_x, self._max_x + 1):
                if (x, y) == (self.drop_start.x, self.drop_start.y):
                    line += '+'
                elif (x, y) == (self.abys.x, self.abys.y):
                    line += 'X'
                elif Coordinate(x, y) in self._sand_coordinates:
                    line += "o"
                elif Coordinate(x, y) in self._coordinates:
                    line += "#"
                else:
                    line += "."
            print(line)
        print()

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

    def _add_intermediate_x(self,
                            from_coordinate: Coordinate,
                            to_coordinate: Coordinate) -> None:
        y = from_coordinate.y
        start = min(from_coordinate.x, to_coordinate.x)
        stop = max(from_coordinate.x, to_coordinate.x) + 1
        for x in range(start, stop):
            self._coordinates.add(Coordinate(x=x, y=y))

    def _add_intermediate_y(self,
                            from_coordinate: Coordinate,
                            to_coordinate: Coordinate) -> None:
        x = from_coordinate.x
        start = min(from_coordinate.y, to_coordinate.y)
        stop = max(from_coordinate.y, to_coordinate.y) + 1
        for y in range(start, stop):
            self._coordinates.add(Coordinate(x=x, y=y))

    def _get_coordinates(self, from_coordinate: Coordinate,
                         to_coordinate: Coordinate) \
            -> set[Coordinate]:
        coordinates: set[Coordinate] = set()
        if from_coordinate.x != to_coordinate.x:
            self._add_intermediate_x(from_coordinate, to_coordinate)
        else:
            self._add_intermediate_y(from_coordinate, to_coordinate)
        return coordinates


def main() -> None:

    cave = Cave("input_files/day14.txt")
    cave._draw_cave()
    # cave._add_row(cave._max_y + 2)
    solution_1 = cave.drop_til_you_drop()
    print(f"{solution_1 = }\n")

    cave._draw_cave()
    #
    # cave._sand_coordinates.clear()
    # cave._draw_cave()
    # solution_2 = cave.drop_til_you_drop()
    # cave._draw_cave()
    # print(f"{solution_2 = }")

if __name__ == "__main__":
    main()

