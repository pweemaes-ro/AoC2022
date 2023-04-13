"""Day 7: No Space Left On Device."""
from __future__ import annotations

import time
from collections import defaultdict
from itertools import accumulate
from typing import Iterable

part_1 = "Find all of the directories with a total size of at most " \
         "100000. What is the sum of the total sizes of those directories?"


part_2 = "Find the smallest directory that, if deleted, would free up " \
         "enough space on the filesystem to run the update. What is the " \
         "total size of that directory?"


class Directory:
    """There is NO NEED to store files, since all we care about is the size of
    directories. See add_filesize!"""

    def __init__(self, parent: Directory | None = None) -> None:
        self.__parent_dir = parent or self
        self.__size = 0
        self.__subdirs: dict[str, Directory] = dict()

    def add_subdir(self, name: str) -> None:
        """Add a subdir with given 'name' to 'self' directory. Note: No check
        whether a sub directory with 'name' already exists! If so, it will be
        overwritten (=> size will be reset to 0)!"""

        self.__subdirs[name] = Directory(self)

    def add_filesize(self, size: int) -> None:
        """Add 'size' to the size of self and (recursively) its parents."""

        self.__size += size

        if self.__parent_dir != self:
            self.__parent_dir.add_filesize(size)

    @property
    def size(self) -> int:
        """Return the size of (files in) 'self' directory."""

        return self.__size

    def get_all_dirs(self) -> Iterable[Directory]:
        """Yield Directories 'self' and all its subdirs."""

        yield self

        for sub_dir in self.__subdirs.values():
            yield from sub_dir.get_all_dirs()

    def sub_dir(self, name: str) -> Directory:
        """Return the subdirectory of 'self' directory with the specified name.
        Note: NO checks whether subdirectory exists. If it does not exist, a
        KeyError will be raised."""

        return self.__subdirs[name]

    @property
    def parent_dir(self) -> Directory:
        """Return the parent directory of this directory."""

        return self.__parent_dir


def build_directory_tree(all_lines: list[str]) -> Directory:
    """Build the directory tree from data in all_lines. Return the root of the
    tree."""

    root = current_dir = Directory()

    for line in all_lines:
        match line.split():
            case "$", "cd", "..":
                current_dir = current_dir.parent_dir
            case "$", "cd", "/":
                current_dir = root
            case "$", "cd", dir_name:
                current_dir = current_dir.sub_dir(dir_name)
            case '$', 'ls':
                pass
            case "dir", dir_name:
                current_dir.add_subdir(dir_name)
            case size, _:
                current_dir.add_filesize(int(size))

    return root


def main() -> None:
    """Solve the puzzle."""

    start = time.perf_counter_ns()

    with open("input_files/day7.txt") as input_file:
        all_lines = input_file.readlines()

    root = build_directory_tree(all_lines)
    all_sizes = list(directory.size for directory in root.get_all_dirs())
    free_needed = root.size - 40_000_000

    solution_1 = sum(filter(lambda size: size <= 100_000, all_sizes))
    solution_2 = min(filter(lambda size: size >= free_needed, all_sizes))

    stop = time.perf_counter_ns()

    assert solution_1 == 1_743_217
    print(f"Day 7 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 8_319_096
    print(f"Day 7 part 2: {part_2} {solution_2:_}")

    print(f"Day 7 took {(stop - start) * 10 ** -6:.3f} ms")


def main_2() -> None:
    """Sublime solution using accumulate to build paths and keep track of
    sizes! Taken from (but slightly changed) https://www.reddit.com/r/
    adventofcode/comments/zesk40/comment/iz8fww6/?utm_source=share&
    utm_medium=web2x&context=3"""

    start = time.perf_counter_ns()

    dirs: dict[str, int] = defaultdict(int)

    with open("input_files/day7.txt") as input_file:
        for line in input_file:
            match line.split():
                case '$', 'cd', '/':
                    curr = ['/']
                case '$', 'cd', '..':
                    curr.pop()
                case '$', 'cd', x:
                    curr.append(x + '/')
                case '$', 'ls':
                    pass
                case 'dir', _:
                    pass
                case size, _:
                    for p in accumulate(curr):
                        dirs[p] += int(size)

    solution_1 = sum(s for s in dirs.values() if s <= 100_000)
    solution_2 = min(s for s in dirs.values() if s >= dirs['/'] - 40_000_000)

    stop = time.perf_counter_ns()

    assert solution_1 == 1_743_217
    print(f"Day 7 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 8_319_096
    print(f"Day 7 part 2: {part_2} {solution_2:_}")

    print(f"Day 7 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
    # Note: solve_all will NOT call main_2(), only calls main().
    main_2()
