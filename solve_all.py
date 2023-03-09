"""Main application to solve all problems. It uses a 'plugin' approach..."""
import glob
from types import ModuleType
from importlib import import_module


def aoc_modules(pattern: str = "Day *.py") -> list[ModuleType]:
    """Return a list of all loaded module objects imported from files in
    current working directory (cwd) that have the pattern.
    """

    # This technique of dynamically importing during modules runtime is also
    # referred to as a 'plugin model'. The loaded modules are functional
    # extensions that are added WITHOUT modifying any code in the project. All
    # it takes to add functionality is adding a file that satisfies a wildcard
    # to a specific location, to have it loaded and executed automaticaly by
    # the solve_all function.
    return sorted([import_module(script_file[:-3])
                   for script_file in glob.iglob(pattern)],
                  key=lambda m: int(m.__name__[4:6]))
    # return [import_module(script_file[:-3])
    #                for script_file in glob.iglob(pattern)]


def solve_all():
    """Solve all available puzzles by calling main on all available (and
    imported) modules."""

    print("*" * 50)
    for module in aoc_modules():
        print(module.__name__)
        module.main()
        print("*" * 50)


if __name__ == "__main__":
    solve_all()
