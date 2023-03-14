"""Day 12: Hill Climbing Algorithm."""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue

from AoCLib.Miscellaneous import Coordinate


class MazeStrategy(ABC):
    """Abstract class for strategy to be used when searching for shortest
    path."""

    def __init__(self, start_pos: Coordinate):
        self._start_pos = start_pos

    @property
    def start_pos(self) -> Coordinate:
        """Return the start position for this strategy."""
        return self._start_pos

    @abstractmethod
    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True when found what we were looking for, else False. Must
        be implemented by concrete classes."""

        ...

    @staticmethod
    def _is_ongrid(matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if coordinate is on the grid, else False."""

        return 0 <= coordinate.x < len(matrix[0]) \
            and 0 <= coordinate.y < len(matrix)

    @abstractmethod
    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True when the step from current to neighbor is allowed
        (notice that this is the last test before a neighbor is accepted, so
        it is on the grid and not already visited before). Must be implemented
        by concrete classes."""

        ...

    @ abstractmethod
    def on_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called wheneven a coordinate is visited."""

        ...


def height_validator(matrix: Matrix,
                     current: Coordinate,
                     neighbor: Coordinate,
                     climbing: bool) -> bool:
    """Checks if stepping from current to neighbor is too steep. If climbing:
    return True iif neighbor is at most one level higher than current.
    If climbing is False: return True if neighbor is at most one level lower
    than current."""

    current_value = matrix.coordinate_value(current)
    neighbor_value = matrix.coordinate_value(neighbor)

    if climbing:
        return neighbor_value - current_value <= 1
    else:
        return current_value - neighbor_value <= 1


class AscendingStrategy(MazeStrategy):
    """Implementation of the strategy for part 1: Finished when the finish_pos
    has been reached, level difference at most 1 assuming climbing."""

    def __init__(self, start_pos: Coordinate, finish_pos: Coordinate):
        super().__init__(start_pos)
        self._finish_pos = finish_pos
        self.visited: set[Coordinate] = set()

    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True if neighbor if 'valid', that is, on grid, not visited
        yet, and not high/low relative to current."""

        if neighbor in self.visited:
            return False

        if not self._is_ongrid(matrix, neighbor):
            return False

        return height_validator(matrix, current, neighbor, climbing=True)

    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if the coordinate is the finish position, else False."""

        return coordinate == self._finish_pos

    # noinspection PyUnusedLocal
    def on_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called wheneven a coordinate is visited."""

        self.visited.add(coordinate)


class DescendingToLowestLevel(MazeStrategy):
    """Implementation of the strategy for part 1: Finished when the finish_pos
    has been reached, level difference at most 1 assuming climbing."""

    def __init__(self, start_pos: Coordinate):
        super().__init__(start_pos)
        self.visited: set[Coordinate] = set()

    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True if neighbor if 'valid', that is, on grid, not visited
        yet, and not high/low relative to current."""

        if neighbor in self.visited:
            return False

        if not self._is_ongrid(matrix, neighbor):
            return False

        return height_validator(matrix, current, neighbor, climbing=False)

    def is_finish(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if matrix content at coordinate is "a"."""

        return matrix[coordinate.y][coordinate.x] == "a"

    # noinspection PyUnusedLocal
    def on_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called wheneven a coordinate is visited."""

        self.visited.add(coordinate)


class Matrix(list):
    """Matrix class is just a list (of strings) with minimal functionalitie."""

    def __init__(self, lines: list[str]):
        super().__init__(lines)

    def coordinate_value(self, coordinate: Coordinate) -> int:
        """Return the ordinol of the char at the given coordinate in the
        matrix."""

        return ord(self[coordinate.y][coordinate.x])

    def replace(self, old: str, new: str) -> Coordinate | None:
        """Find the first occurence of old in the maze's matrix, replace it
        with new, and return the replacement coordinate."""

        for y in range(len(self)):
            if (x := self[y].find(old)) != -1:
                self[y] = self[y].replace(old, new)
                return Coordinate(x, y)

        return None


@dataclass
class Maze:
    """Class representing a maze. The matrix holds the content (str's of
    length 1). Searching uses an instance of a MazeStrategy concrete class."""

    matrix: Matrix

    def get_neigbors(self, current: Coordinate, strategy: MazeStrategy) \
            -> list[Coordinate]:
        """Return a list of all neighbors of current coordinate that should be
        visited as part of path finding. Decision whether neighbor should be
        visited is made in the strategy.neighbo_ok methdd."""

        return [neighbor
                for neighbor in [
                    Coordinate(current.x - 1, current.y),
                    Coordinate(current.x + 1, current.y),
                    Coordinate(current.x, current.y - 1),
                    Coordinate(current.x, current.y + 1),
                ]
                if strategy.neighbor_ok(self.matrix, current, neighbor)]

    def find_shortest_path(self, strategy: MazeStrategy) -> int | None:
        """Find and return the length of the shortest path in the maze from its
        start location to it finish location. Return None if there was no such
        path"""

        start_pos = strategy.start_pos
        strategy.on_visit(self.matrix, start_pos)
        paths_queue: Queue[tuple[Coordinate, int]] = Queue()
        paths_queue.put((start_pos, 0))

        while paths_queue.qsize():
            current_coordinate, current_steps = \
                paths_queue.get()

            for neighbor in self.get_neigbors(current_coordinate, strategy):
                if strategy.is_finish(self.matrix, neighbor):
                    return current_steps + 1

                strategy.on_visit(self.matrix, neighbor)
                paths_queue.put((neighbor, current_steps + 1))

        return None


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

    solution_1 = maze.find_shortest_path(AscendingStrategy(start_pos,
                                                           finish_pos))

    # Finding the shortest path for ANY "a" to the finish position is
    # equivalent to finding the shortest path from the finish position to
    # any "a".
    solution_2 = maze.find_shortest_path(DescendingToLowestLevel(finish_pos))

    stop = time.perf_counter_ns()

    assert solution_1 == 380
    print(f"Day 12 part 1: {part_1} {solution_1}")

    assert solution_2 == 375
    print(f"Day 12 part 2: {part_2} {solution_2}")

    print(f"Day 12 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
