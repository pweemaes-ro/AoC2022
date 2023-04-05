"""Day 8: Treetop Tree House."""
import time
from dataclasses import dataclass, field
from math import prod

from AoCLib.Miscellaneous import transposed


@dataclass
class Tree:
    """A simple dataclass. Height is the value in the input. Visible is True
    if the tree is visible from one or more sides."""

    height: int
    scenic_score: int = 0
    visible: bool = False
    scenic_scores: list[int] = field(default_factory=list)


TreeRow = list[Tree]
TreeMatrix = list[TreeRow]


def _get_scenic_score(tree: Tree, other_trees: TreeRow) -> int:
    """Return the scenic score for the tree. This is the nr of trees until a
    larger or equally large tree is encountered."""

    score = 0

    for other_tree in other_trees:
        score += 1
        if tree.height <= other_tree.height:
            break

    return score


def _set_visibility(tree: Tree, largest_height_so_far: int) -> int:
    """Set tree visibility to True if tree is higher than the highest tree
    in the row so far. Return (the possibly new value for) the height of the
    highest tree in the row"""

    if tree.height > largest_height_so_far:
        largest_height_so_far = tree.height
        tree.visible = True
    return largest_height_so_far


def _process_directed_row(tree_row: TreeRow) -> None:
    """Process trees in the row (from left to right only!)."""

    row_length = len(tree_row)
    highest_tree_in_row = -1

    for i, tree in enumerate(tree_row, start=1):
        highest_tree_in_row = _set_visibility(tree, highest_tree_in_row)
        other_trees = tree_row[i: row_length]
        score = _get_scenic_score(tree, other_trees)
        tree.scenic_scores.append(score)


def _process_row(matrix_row: TreeRow) -> None:
    """Process the row by delegating to _process_directed_row for original row
    AND the reversed row."""
    
    for directed_treerow in (matrix_row, matrix_row[::-1]):
        _process_directed_row(directed_treerow)


def _process_matrix(matrix: TreeMatrix) -> None:
    """Checks and sets tree visibility of the trees in the matrix by 
    delegating to _process_row for each row."""

    for tree_row in matrix:
        _process_row(tree_row)


def _update_scenic_score_products(matrix: TreeMatrix) -> None:
    """Calculates and sets the product of the tree's 4 scenics scores."""

    for tree_row in matrix:
        for tree in tree_row:
            tree.scenic_score = prod(tree.scenic_scores)


def get_max_scenic_score(matrix: TreeMatrix) -> int:
    """Return the maximum scenic score found in the matric of trees."""

    return max([tree.scenic_score for tree_row in matrix for tree in tree_row])


def count_visible_trees(matrix: TreeMatrix) -> int:
    """Return the nr of trees visible from the outside."""

    return sum(tree.visible for row in matrix for tree in row)


def set_visibility_and_scores(matrix: TreeMatrix) -> None:
    """Sets all relevant data members of each tree (visibility, scenic scores,
    the product of the scenic scores."""

    for directed_matrix in (matrix, transposed(matrix)):
        _process_matrix(directed_matrix)

    _update_scenic_score_products(matrix)


def build_matrix(lines: list[str]) -> TreeMatrix:
    """Build a matrix of trees with height according to data in lines. Notice
    that all lines have "\n" so ignore last char on each line."""

    return [[Tree(int(s)) for s in line[:-1]] for line in lines]


def main() -> None:
    """Solve the puzzle."""

    part_1 = "Consider your map; how many trees are visible from outside " \
             "the grid?"
    part_2 = "Consider each tree on your map. What is the highest scenic " \
             "score possible for any tree?"

    start = time.perf_counter_ns()

    with open("input_files/day8.txt") as input_file:
        lines = input_file.readlines()

    matrix = build_matrix(lines)
    set_visibility_and_scores(matrix)

    solution_1 = count_visible_trees(matrix)
    solution_2 = get_max_scenic_score(matrix)

    stop = time.perf_counter_ns()

    assert solution_1 == 1543
    print(f"Day 8 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 595080
    print(f"Day 8 part 2: {part_2} {solution_2:_}")

    print(f"Day 8 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
