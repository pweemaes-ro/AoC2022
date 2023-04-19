"""Day 12: Hill Climbing Algorithm."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from typing import TypeAlias, Optional, IO

# type aliases
Coordinate: TypeAlias = tuple[int, int]


class MazeStrategy(ABC):
    """Abstract class for strategy to be used when BFS searching for a path."""

    def __init__(self, start_pos: Coordinate) -> None:
        self.__start_pos = start_pos

    @property
    def start_pos(self) -> Coordinate:
        """Return the start position for this strategy."""

        return self.__start_pos

    @abstractmethod
    def finish_reached(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True when found what we were looking for, else False. Must
        be implemented by concrete classes."""

        ...

    @staticmethod
    def _is_ongrid(matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if coordinate is on the grid, else False."""

        return 0 <= coordinate[0] < len(matrix[0]) \
            and 0 <= coordinate[1] < len(matrix)

    @abstractmethod
    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True when the step from current to neighbor is allowed. Must
        be implemented by concrete classes."""

        ...

    @ abstractmethod
    def register_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called whenever a coordinate is visited. Must be implemented by
        concrete class."""

        ...


def height_validator(matrix: Matrix,
                     current: Coordinate,
                     neighbor: Coordinate,
                     climbing: bool) -> bool:
    """Checks if stepping from current to neighbor is too steep. If climbing:
    return True if and only if neighbor is at most one level higher than
    current, else return False. If climbing is False: return True if an only
    if neighbor is at most one level lower than current, else return False."""

    current_value = matrix.coordinate_value(current)
    neighbor_value = matrix.coordinate_value(neighbor)

    if climbing:
        return neighbor_value - current_value <= 1
    else:
        return current_value - neighbor_value <= 1


class AscendingStrategy(MazeStrategy):
    """Implementation of the strategy for part 1: Finished when the finish_pos
    has been reached, level difference at most 1 assuming climbing."""

    def __init__(self, start_pos: Coordinate, finish_pos: Coordinate) -> None:
        super().__init__(start_pos)
        self._finish_pos = finish_pos
        self.visited: set[Coordinate] = set()

    def neighbor_ok(self,
                    matrix: Matrix,
                    current: Coordinate,
                    neighbor: Coordinate) -> bool:
        """Return True if neighbor is 'valid', that is, on grid, not visited
        yet, and not high/low relative to current."""

        if neighbor in self.visited:
            return False

        if not self._is_ongrid(matrix, neighbor):
            return False

        return height_validator(matrix, current, neighbor, climbing=True)

    def finish_reached(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if the coordinate is the finish position, else False."""

        return coordinate == self._finish_pos

    # noinspection PyUnusedLocal
    def register_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called whenever a coordinate is visited. Keep track of all visited
        coordinates so we don't go there twice..."""

        self.visited.add(coordinate)


class DescendingToLowestLevel(MazeStrategy):
    """Implementation of the strategy for part 2: Finished when a coordinate
    with ord("a") = 97 has been reached, level difference at most 1 assuming
    descending."""

    def __init__(self, start_pos: Coordinate) -> None:
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

    def finish_reached(self, matrix: Matrix, coordinate: Coordinate) -> bool:
        """Return True if matrix content at coordinate is ord("a") = 97."""

        return matrix[coordinate[1]][coordinate[0]] == 97   # 97 = ord("a")

    # noinspection PyUnusedLocal
    def register_visit(self, matrix: Matrix, coordinate: Coordinate) -> None:
        """Called whenever a coordinate is visited. Keep track of all visited
        coordinates so we don't go there twice..."""

        self.visited.add(coordinate)


# class Matrix(list[str]):
class Matrix(list[list[int]]):
    """A Matrix is a list of rows, each row is a list of ints (ordinal values
    of the chars in the input lines). It has very limited functionality..."""

    def __init__(self, lines: list[str]) -> None:
        super().__init__(list(ord(c) for c in line) for line in lines)

    def coordinate_value(self, coordinate: Coordinate) -> int:
        """Return the ordinol of the char at the given coordinate in the
        matrix."""

        return self[coordinate[1]][coordinate[0]]

    def replace(self, old: int, new: int) -> Optional[Coordinate]:
        """Find the first occurence of 'old' in the matrix, replace it with
        'new', and return the replacement coordinate. The matrix is searched
        from top row to bottom row, each row from left to right. Return None
        if 'old' not found."""

        for y in range(len(self)):
            if old in self[y]:
                x = self[y].index(old)
                self[y][x] = new
                return x, y
        return None


@dataclass
class Maze:
    """Class representing a maze. The matrix holds the content (integers,
    representing the ordinal values of the chars in the input). Searching uses
    an instance of a MazeStrategy concrete class."""

    matrix: Matrix

    def get_neigbors(self, current: Coordinate, strategy: MazeStrategy) \
            -> list[Coordinate]:
        """Return a list of all neighbors of current coordinate that should be
        visited as part of path finding. Decision whether neighbor should be
        visited is made in the strategy's neighbor_ok() method."""

        return [neighbor
                for neighbor in [
                    (current[0] - 1, current[1]),
                    (current[0] + 1, current[1]),
                    (current[0], current[1] - 1),
                    (current[0], current[1] + 1),
                ]
                if strategy.neighbor_ok(self.matrix, current, neighbor)]

    def find_shortest_path(self, strategy: MazeStrategy) -> Optional[int]:
        """Find and return the length of the shortest path in the maze from its
        start location until the finish is reached. What constitutes reaching
        the finish is determined by the strategy's is_finish() method."""

        start_pos = strategy.start_pos
        strategy.register_visit(self.matrix, start_pos)
        paths_queue: Queue[tuple[Coordinate, int]] = Queue()
        paths_queue.put((start_pos, 0))

        while paths_queue.qsize():
            current_coordinate, current_steps = paths_queue.get()

            for neighbor in self.get_neigbors(current_coordinate, strategy):
                if strategy.finish_reached(self.matrix, neighbor):
                    return current_steps + 1

                strategy.register_visit(self.matrix, neighbor)
                paths_queue.put((neighbor, current_steps + 1))

        return None


def get_maze(file: IO[str]) -> Maze:
    """Return an initialized maze, constructed from data in the input file."""

    return Maze(Matrix(file.read().splitlines()))


def main() -> None:
    """Solve the puzzle."""

    part_1 = "What is the fewest steps required to move from your current " \
             "position to the location that should get the best signal?"
    part_2 = "What is the fewest steps required to move starting from any " \
             "square with elevation a to the location that should get the " \
             "best signal?"

    start = time.perf_counter_ns()

    with open("input_files/day12.txt") as input_file:
        maze = get_maze(input_file)

    start_pos = maze.matrix.replace(ord("S"), ord("a"))
    finish_pos = maze.matrix.replace(ord("E"), ord("z"))
    solution_1 = solution_2 = None
    if start_pos and finish_pos:
        solution_1 = maze.find_shortest_path(AscendingStrategy(start_pos,
                                                               finish_pos))

        # Finding the shortest path for ANY "a" to the finish position is
        # equivalent to finding the shortest path from the finish position to
        # any "a".
        solution_2 = maze.find_shortest_path(
            DescendingToLowestLevel(finish_pos))

    stop = time.perf_counter_ns()

    assert solution_1 == 380
    print(f"Day 12 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 375
    print(f"Day 12 part 2: {part_2} {solution_2:_}")

    print(f"Day 12 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
