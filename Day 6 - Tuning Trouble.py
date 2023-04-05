"""Day 6: Tuning Trouble"""
import time
from collections import deque
from typing import IO


def _get_first_non_unique_pos(text: deque) -> int:
    """Returns the (zero-based) position of the FIRST occurance of a
    non-unique char in text. A return value of -1 indicates all characters in
    text are unique."""

    for i in range(len(text) - 1):
        for j in range(i + 1, len(text)):
            if text[i] == text[j]:
                return i
    return -1


def _pos_after_all_unique_chunk(stream: IO, chunksize: int) -> int:
    """Return the position right after a chunk of size chunksize of unique
    chars was found in the stream. Assumes there is such a chunk (no error-
    handling if EOF!)"""

    chunk = deque(stream.read(chunksize), maxlen=chunksize)

    while (first_non_unique_pos := _get_first_non_unique_pos(chunk)) != -1:
        chunk.extend(stream.read(first_non_unique_pos + 1))

    return stream.tell()


def processed_before_package_detected(stream: IO) -> int:
    """Return nr of chars processed before a start-of-package marker is
    detected. A return value of 0 indicates no start-of-package was found."""

    return _pos_after_all_unique_chunk(stream, chunksize=4)


def processed_before_message_detected(stream: IO) -> int:
    """Return nr of chars processed before a start-of-message
    marker is detected. A value of 0 indicates no start-of-message was found.
    """

    return _pos_after_all_unique_chunk(stream, chunksize=14)


def main() -> None:
    """Solve the puzzle."""

    # It is assumed (and consistent with the problem description) that the
    # start-of-message marker starts AFTER the start-of-package marker.

    part_1 = "How many characters need to be processed before the first " \
             "start-of-packet marker is detected?"
    part_2 = "How many characters need to be processed before the first " \
             "start-of-message marker is detected?"

    start = time.perf_counter_ns()

    with open("input_files/day6.txt") as my_stream:
        solution_1 = processed_before_package_detected(my_stream)
        solution_2 = processed_before_message_detected(my_stream)

    stop = time.perf_counter_ns()

    assert solution_1 == 1175
    print(f"Day 6 part 1: {part_1} {solution_1:_}")

    assert solution_2 == 3217
    print(f"Day 6 part 2: {part_2} {solution_2:_}")

    print(f"Day 6 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
