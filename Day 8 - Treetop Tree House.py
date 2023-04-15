"""Day 8: Treetop Tree House."""
import time
from dataclasses import dataclass
from typing import TypeAlias

from Matrices import transposed


@dataclass
class Tree:
    """A simple dataclass representing a tree and a few methods."""

    height: int
    scenic_score = 1
    visible = False

    def set_tree_visibility(self, height_to_beat: int) -> int:
        """Set the visibility of the tree. Return the height to beat for the
        next tree in the same row."""

        # Note: This solution calculates the visibility of each tree for each
        # direction (from the right, left, top or bottom). Strictly speaking,
        # once a tree is visible from one direction, there's no need to check
        # its visibility from any remaining directories. There's no point in
        # checking this, since we always need to check if self.height >
        # height_to_beat, even if the tree's visibility is already set to True.

        if 9 != height_to_beat < self.height:
            height_to_beat = self.height
            self.visible = True

        return height_to_beat

    def update_scenic_score(self, other_trees: list["Tree"]) -> None:
        """Return the scenic score for the tree. This is the nr of trees until
        a larger or equally large tree is encountered."""

        score = 0

        for other_tree in other_trees:
            score += 1
            if self.height <= other_tree.height:
                break

        if score:
            self.scenic_score *= score


# type aliases
TreeRow: TypeAlias = list["Tree"]
TreeMatrix: TypeAlias = list[TreeRow]


def get_max_scenic_score(matrix: TreeMatrix) -> int:
    """Return the maximum scenic score found in the matric of trees."""

    return max([tree.scenic_score
                for tree_row in matrix
                for tree in tree_row])


def count_visible_trees(matrix: TreeMatrix) -> int:
    """Return the nr of trees visible from the outside."""

    # We take advantage of the fact that True == 1 and False == 0
    return sum(tree.visible
               for row in matrix
               for tree in row)


def _process_tree_row(tree_row: TreeRow) -> None:
    """Process trees in the row (from left to right only!)."""

    height_to_beat = -1
    for i, tree in enumerate(tree_row, start=1):
        height_to_beat = tree.set_tree_visibility(height_to_beat)
        tree.update_scenic_score(tree_row[i:])


def process_forest(forest_matrix: TreeMatrix) -> None:
    """Sets visibility and scenis_score of each tree."""

    for row, col in zip(forest_matrix, transposed(forest_matrix)):
        for direction in (row, row[::-1], col, col[::-1]):
            _process_tree_row(direction)


def build_forest_matrix(lines: list[str]) -> TreeMatrix:
    """Build a matrix of trees with height according to data in lines."""

    return [[Tree(int(s)) for s in line] for line in lines]


def main() -> None:
    """Solve the puzzle."""

    part_1 = "Consider your map; how many trees are visible from outside " \
             "the grid?"
    part_2 = "Consider each tree on your map. What is the highest scenic " \
             "score possible for any tree?"

    start = time.perf_counter_ns()

    with open("input_files/day8.txt") as input_file:
        lines = input_file.read().splitlines()

    forest_matrix = build_forest_matrix(lines)
    process_forest(forest_matrix)

    solution_1 = count_visible_trees(forest_matrix)
    solution_2 = get_max_scenic_score(forest_matrix)

    stop = time.perf_counter_ns()

    assert solution_1 == 1543
    print(f"Day 8 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 595080
    print(f"Day 8 part 2: {part_2} {solution_2:_}")

    print(f"Day 8 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
