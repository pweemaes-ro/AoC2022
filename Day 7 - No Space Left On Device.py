"""Day 7: No Space Left On Device."""
from __future__ import annotations

import time
from enum import StrEnum
from functools import wraps
from collections.abc import Callable


class Command(StrEnum):
    """The commands + a command marker that are currently supported."""

    COMMAND_MARKER = "$"
    CHANGE_DIR = "cd"
    LIST = "ls"


class FSO:
    """The nodes for a File System (files and directories)."""

    class FsoTypes(StrEnum):
        """The following types are currently supported in a fso tree."""

        DIR = "dir"
        FILE = "file"

    class FsoDirs(StrEnum):
        """The following special directory names are currently supported in a
        fso tree."""

        ROOT = "/"
        PARENT = ".."

    def __init__(self, name: str, fso_type: FsoTypes, size: int = 0) -> None:
        self._name = name
        self._parent: FSO = self
        self._type = fso_type
        self._size = 0 if type == FSO.FsoTypes.DIR else size
        self._children: list[FSO] = []
        self._dirty = False

    @property
    def name(self) -> str:
        """Return the name of this fso."""

        return self._name

    @property
    def fso_size(self) -> int:
        """Return the size of this fso."""

        if self._type == FSO.FsoTypes.DIR:
            if self._dirty:
                self._size = sum(child.fso_size for child in self._children)
                self._set_dirty(False)

        return self._size

    @property
    def fso_type(self) -> FSO.FsoTypes:
        """Return the type ("file" or "dir") of the fso."""

        return self._type

    @property
    def parent(self) -> FSO:
        """Return the parent dir of this fso."""

        return self._parent

    def is_root(self) -> bool:
        """Return True if this is the root fso object (the only one for which
        the parent is itself."""

        return self._parent == self

    def add(self, component: FSO) -> None:
        """Add component as child to this fso. Note: No check whether child
        with same name as component already exists!"""

        self._children.append(component)
        component._parent = self
        self._set_dirty(True)

    def collect(self, filter_func: Callable) -> list[FSO]:
        """Return a list of all items (incl. self) that satisfy the filter."""

        fso_list = []
        if filter_func(self):
            fso_list.append(self)

        for child in self._children:
            fso_list.extend(child.collect(filter_func))

        return fso_list

    def _set_dirty(self, dirty: bool):
        """If dirty == True. sets this fso and all parent dirs up to the root
        directory 'dirty' to indicate that fso_sizes of these dirs must be
        recalculated when fso_size is queried. If dirty is False, the dirty
        flag is cleared for this fso (but not for its parent dirs)."""

        self._dirty = dirty
        if dirty and not self.is_root():
            self._parent._set_dirty(dirty)

    def child(self, name: str):
        """Return the child of this fso with the specified name."""

        for child in self._children:
            if child._name == name:
                return child

        raise ValueError(f"Directory '{self._name}' has no child '{name}'.")

    @property
    def root(self) -> FSO:
        """Return the root of the fso."""
        fso = self
        while not fso.is_root():
            fso = fso._parent
        return fso


def dirs_le_size(size: int) -> Callable[[FSO], bool]:
    """Filter function. Only dirs with fso_size <= size."""

    @wraps(dirs_le_size)
    def _filter_func(fso: FSO) -> bool:
        return fso.fso_size <= size \
            and fso.fso_type == FSO.FsoTypes.DIR
    return _filter_func


def dirs_ge_size(size: int) -> Callable[[FSO], bool]:
    """Filter function. Only dirs with fso_size >= size."""

    @wraps(dirs_ge_size)
    def _filter_func(fso: FSO) -> bool:
        return fso.fso_size >= size \
            and fso.fso_type == FSO.FsoTypes.DIR
    return _filter_func


def _process_cd(current_dir: FSO, param: str) -> FSO:

    if param == FSO.FsoDirs.ROOT:
        return current_dir.root
    elif param == FSO.FsoDirs.PARENT:
        return current_dir.parent
    elif len(param):
        return current_dir.child(param)
    else:
        raise ValueError(f"Unexpected empty param for cd command!")


def _add_fso(current_dir: FSO, size_or_dir: str, name: str) -> None:
    if size_or_dir == FSO.FsoTypes.DIR:
        current_dir.add(FSO(name, FSO.FsoTypes.DIR))
    else:
        current_dir.add(FSO(name, FSO.FsoTypes.FILE, int(size_or_dir)))


def build_fso_tree(all_lines: list[str], current_dir: FSO) -> None:
    """Build the fso tree from data in all_lines."""

    for line in all_lines:
        terms = line.split()

        match terms[0]:
            case Command.COMMAND_MARKER:
                match terms[1]:
                    case Command.CHANGE_DIR:
                        current_dir = _process_cd(current_dir, terms[2])
                    case Command.LIST:
                        pass
                    case _:
                        raise ValueError(f"Unrecognized command: '{terms[1]}'")
            case _:     # output from the last command
                _add_fso(current_dir, terms[0], terms[1])


def main() -> None:
    """Solve the puzzle."""

    part_1 = "Find all of the directories with a total size of at most " \
             "100000. What is the sum of the total sizes of those directories?"

    part_2 = "Find the smallest directory that, if deleted, would free up " \
             "enough space on the filesystem to run the update. What is the " \
             "total size of that directory?"

    start = time.perf_counter_ns()
    with open("input_files/day7.txt") as input_file:
        all_lines = input_file.readlines()

    root = FSO(FSO.FsoDirs.ROOT, FSO.FsoTypes.DIR)
    build_fso_tree(all_lines, root)

    solution_1 = sum(fso.fso_size
                     for fso in root.collect(dirs_le_size(100_000)))

    must_free = 30_000_000 - (70_000_000 - root.fso_size)
    solution_2 = min([fso.fso_size
                      for fso in root.collect(dirs_ge_size(must_free))])

    stop = time.perf_counter_ns()

    assert solution_1 == 1743217
    print(f"Day 7 part 1: {part_1} {solution_1}")

    assert solution_2 == 8319096
    print(f"Day 7 part 2: {part_2} {solution_2}")

    print(f"Day 7 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
