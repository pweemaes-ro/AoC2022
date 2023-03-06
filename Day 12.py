"""Day 12: Hill Climbing Algorithm."""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from queue import Queue


class MazeStrategy(ABC):
    """Abstract class for strategy to be used when searching for shortest
    path."""

    @abstractmethod
    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return true when found what we were looking for, else False. Must
        be implemented by concrete classes."""

        ...

    @abstractmethod
    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return true when the step from current to neighbor is allowed
        (notice that this is the last test before a neighbor is accepted, so
        it is on the grid and not already visited before). Must be implemented
        by concrete classes."""

        ...


def neighbor_validator(matrix: Matrix,
                       current: Coordinate,
                       neighbor: Coordinate,
                       climbing: bool) -> bool:
    """Checks if stepping from current to neighbor is too steep
    (neighbor may not be more than 1 level higher than current).
    If climbing (in closure) is False, then returns True iif the
    descent is at most 1."""

    current_value = ord(matrix[current.y][current.x])
    neighbor_value = ord(matrix[neighbor.y][neighbor.x])
    if not climbing:
        return current_value - neighbor_value <= 1
    else:
        return neighbor_value - current_value <= 1


class AToZStrategy(MazeStrategy):
    """Implementation of the strategy for part 1: Finished when the finish_pos
    has been reached, level difference at most 1 assuming climbing."""

    def __init__(self, finish_pos: Coordinate):
        self._finish_pos = finish_pos

    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True if neighbor is at most one level higher than current,
        else False."""

        return neighbor_validator(matrix, current, neighbor, climbing=True)

    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if the coordinate is the finish position, else False."""

        return coordinate == self._finish_pos


class ZToAStrategy(MazeStrategy):
    """Implementation of the strategy for part 1: Finished when the finish_pos
    has been reached, level difference at most 1 assuming climbing."""

    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True if neighbor is at most one level lower than current,
        else False."""

        return neighbor_validator(matrix, current, neighbor, climbing=False)

    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if matrix content at coordinate is "a" """

        return matrix[coordinate.y][coordinate.x] == "a"


@dataclass
class Coordinate:
    """A simple coordinate class that is hashable (so we can store coordinates
    in a set)."""

    x: int
    y: int

    def __hash__(self):
        return hash(repr(self))


class Matrix(list):
    """Matrix class is just a list (of strings) with minimal functionalitie."""

    def __init__(self, lines):
        super().__init__(lines)

    def find(self, start: Coordinate, search_for: str) -> Coordinate | None:
        """Find the first occurence of search_for starting at start coordinate.
        If found, return found location as a coordinate, else return None."""

        for y in range(start.y, len(self)):
            x_offset = start.x if y == start.y else 0
            search_in = self[y][x_offset:]
            if (x := search_in.find(search_for)) != -1:
                return Coordinate(x + (start.x if y == start.y else 0), y)

    def replace(self, old: str, new: str) -> Coordinate | None:
        """Find the first occurence of old in the maze's matrix, replace it
        with new, and return the replacement coordinate."""

        for y in range(len(self)):
            if (x := self[y].find(old)) != -1:
                self[y] = self[y].replace(old, new)
                return Coordinate(x, y)


@dataclass
class Maze:
    """Class representing a maze, with start and finish coordinates and a set
    of already visited coordinates."""

    matrix: Matrix = field(default_factory=Matrix)
    visited: set[Coordinate] = field(default_factory=set)

    def _is_ongrid(self, coordinate: Coordinate) -> bool:
        """Return True if coordinate is on the grid, else False."""

        return 0 <= coordinate.x < len(self.matrix[0]) \
            and 0 <= coordinate.y < len(self.matrix)

    def _get_value(self, coordinate: Coordinate) -> int:
        """Return the value of the matrix at the coordinate."""

        return ord(self.matrix[coordinate.y][coordinate.x])

    def get_neigbors(self, current: Coordinate, strategy: MazeStrategy) \
            -> list[Coordinate]:
        """Return a list of all neighbors of current coordinate that should be
        visited as part of path finding. Each such neighbor is
        - on the grid,
        - not visited before,
        - has value <= current value + 1"""

        neighbors = []

        for neighbor in [
            Coordinate(current.x - 1, current.y),
            Coordinate(current.x + 1, current.y),
            Coordinate(current.x, current.y - 1),
            Coordinate(current.x, current.y + 1),
        ]:
            if not self._is_ongrid(neighbor):
                continue

            if neighbor in self.visited:
                continue

            if not strategy.neighbor_ok(self.matrix, current, neighbor):
                continue

            neighbors.append(neighbor)

        return neighbors

    def find_shortest_path(self,
                           start: Coordinate,
                           strategy: MazeStrategy):
        """Find and return the length of the shortest path in the maze from its
        start location to it finish location. Return None if there was no such
        path"""

        self.visited = {start}
        paths_queue = Queue()
        paths_queue.put((start, 0))

        while paths_queue.qsize():
            current_coordinate, current_steps = \
                paths_queue.get()

            for neighbor in self.get_neigbors(current_coordinate, strategy):
                if strategy.is_finish(self.matrix, neighbor):
                    return current_steps + 1

                self.visited.add(neighbor)
                paths_queue.put((neighbor, current_steps + 1))


def get_maze(file: str) -> Maze:
    """Return an initialized maze, constructed from data in the input file."""

    with open(file) as input_file:
        lines = input_file.readlines()

    return Maze(Matrix([line[:-1] for line in lines]))


def main():
    """Solve the puzzle."""

    part_1 = "What is the fewest steps required to move from your current " \
             "position to the location that should get the best signal?"
    part_2 = "What is the fewest steps required to move starting from any " \
             "square with elevation a to the location that should get the " \
             "best signal?"

    start = time.perf_counter_ns()

    maze = get_maze("input_files/day12.txt")

    start_pos = maze.matrix.replace("S", "a")
    finish_pos = maze.matrix.replace("E", "z")

    solution_1 = maze.find_shortest_path(start_pos, AToZStrategy(finish_pos))
    solution_2 = maze.find_shortest_path(finish_pos, ZToAStrategy())

    stop = time.perf_counter_ns()

    assert solution_1 == 380
    print(f"Day 12 part 1: {part_1} {solution_1}")

    assert solution_2 == 375
    print(f"Day 12 part 2: {part_2} {solution_2}")

    print(f"Day 12 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
