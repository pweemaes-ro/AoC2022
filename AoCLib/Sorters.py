"""Sorter classes."""
from abc import abstractmethod, ABC
from typing import Protocol, Self
from typing import TypeVar


# Please note: The code in the concrete classes is NOT mine, I took it from
# the "geeks for geeks" website (and modified it slightly to accomodate my
# specific needs).


class SupportsGreaterThan(Protocol):
    """Items can be sorted with any of the concrete implementations if the
    item class supports all methods in this protocol."""

    @abstractmethod
    def __gt__(self, other: Self) -> bool:
        raise NotImplemented


SupportsSorterStrategy = TypeVar("SupportsSorterStrategy",
                                 bound=SupportsGreaterThan)


class SorterStrategy(ABC):
    """Abstract Base Class for sorter classes (strategies)."""

    @abstractmethod
    def sort(self, data: list[SupportsSorterStrategy]) -> None:
        """Sort the data in place"""
        raise NotImplemented


class InsertionSort(SorterStrategy):
    """Insertion Sort implementation."""

    def sort(self, data: list[SupportsSorterStrategy]) -> None:
        """Sort the data in place using Insertion Sort."""
        # Traverse through 1 to len(data)
        for i in range(1, len(data)):

            key = data[i]

            # Move elements of data[0..i-1], that are
            # greater than key, to one position ahead
            # of their current position
            j = i - 1
            while j >= 0 and key < data[j]:
                data[j + 1] = data[j]
                j -= 1
            data[j + 1] = key


class BubbleSort(SorterStrategy):
    """Bubble Sort implementation."""

    def sort(self, data: list[SupportsSorterStrategy]) -> None:
        """Sort the data in place using slightly modified bubble sort. "Swap
        if the element found is greater than the next element" is changed to
        "Swap if the element found is not smaller than the next element"
        (reason: Packet implements the '<' operator, not the '>' operator."""

        nr_of_items = len(data)

        # Traverse through all list elements
        for i in range(nr_of_items):

            # Last i elements are already in place

            for j in range(nr_of_items - i - 1):

                # traverse the array from 0 to nr_of_packets - i - 1
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]


class MergeSort(SorterStrategy):
    """Merge Sort implementation."""

    def sort(self, data: list[SupportsSorterStrategy]) -> None:
        """Sort the data in place using Merge Sort."""
        if len(data) > 1:

            # Finding the mid of the array
            mid = len(data) // 2

            # Dividing the array elements
            left = data[:mid]

            # into 2 halves
            right = data[mid:]

            # Sorting the first half
            self.sort(left)

            # Sorting the second half
            self.sort(right)

            i = j = k = 0

            # Copy data to temp arrays L[] and R[]
            while i < len(left) and j < len(right):
                if right[j] < left[i]:
                    data[k] = right[j]
                    j += 1
                else:
                    data[k] = left[i]
                    i += 1
                k += 1

            # Checking if any element was left
            while i < len(left):
                data[k] = left[i]
                i += 1
                k += 1

            while j < len(right):
                data[k] = right[j]
                j += 1
                k += 1


class QuickSort(SorterStrategy):
    """Quick Sort implementation."""

    def sort(self, data: list[SupportsSorterStrategy]) -> None:
        """Sort the data in place using Quicksort."""
        self._quick_sort(data, 0, len(data) - 1)

    def _quick_sort(self,
                    array: list[SupportsSorterStrategy],
                    low: int,
                    high: int) -> None:
        if low < high:
            # Find pivot element such that
            # element smaller than pivot are on the left
            # element greater than pivot are on the right
            pi = self._partition(array, low, high)

            # Recursive call on the left of pivot
            self._quick_sort(array, low, pi - 1)

            # Recursive call on the right of pivot
            self._quick_sort(array, pi + 1, high)

    @staticmethod
    def _partition(data: list[SupportsSorterStrategy], low: int, high: int) \
            -> int:
        # Choose the rightmost element as pivot
        pivot = data[high]

        # Pointer for greater element
        i = low - 1

        # Traverse through all elements
        # compare each element with pivot
        for j in range(low, high):
            if pivot > data[j]:
                # If element smaller than pivot is found
                # swap it with the greater element pointed by i
                i += 1

                # Swapping element at i with element at j
                data[i], data[j] = data[j], data[i]

        # Swap the pivot element with
        # e greater element specified by i
        data[i + 1], data[high] = data[high], data[i + 1]

        # Return the position from where partition is done
        return i + 1


if __name__ == "__main__":
    pass
