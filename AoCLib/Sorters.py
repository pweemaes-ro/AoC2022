"""Sorter classes."""
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar


class SupportedBySorter(Protocol):
    """Items can be sorted with any of the concrete implementations if the
    item class supports all methods in this protocol."""

    def __lt__(self, other) -> bool:
        pass


T = TypeVar("T", bound=SupportedBySorter)


class SorterStrategy(ABC):
    """Abstract class for sorter classes."""

    @abstractmethod
    def __call__(self, data: list[T]) -> None:
        ...


class InsertionSort(SorterStrategy):
    """Insertion Sort implementation."""

    def __call__(self, data: list[T]) -> None:
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
    """Insertion Sort implementation."""

    def __call__(self, data: list[T]) -> None:
        """Slightly modified bubble sort. "Swap if the element found is greater
        than the next element" is changed to "Swap if the element found is
        not smaller than the next element" (reason: Packet implements the '<'
        operator, not the '>' operator."""

        nr_of_items = len(data)

        # Traverse through all list elements
        for i in range(nr_of_items):

            # Last i elements are already in place

            for j in range(nr_of_items - i - 1):

                # traverse the array from 0 to nr_of_packets - i - 1
                # (Swap if the element found is "greater than" changed to "not
                # smaller than").
                if not data[j] < data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]


class MergeSort(SorterStrategy):
    """Insertion Sort implementation."""

    def __call__(self, data: list[T]) -> None:
        if len(data) > 1:

            # Finding the mid of the array
            mid = len(data) // 2

            # Dividing the array elements
            left = data[:mid]

            # into 2 halves
            right = data[mid:]

            # Sorting the first half
            self(left)

            # Sorting the second half
            self(right)

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
    """Insertion Sort implementation."""

    def __call__(self, data: list[T]) -> None:
        self._quick_sort(data, 0, len(data) - 1)

    def _quick_sort(self, array, low, high):
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
    def _partition(data: list[T], low: int, high: int):
        # Choose the rightmost element as pivot
        pivot = data[high]

        # Pointer for greater element
        i = low - 1

        # Traverse through all elements
        # compare each element with pivot
        for j in range(low, high):
            # if data[j] <= pivot:
            if not pivot < data[j]:
                # If element smaller than pivot is found
                # swap it with the greater element pointed by i
                # i = i + 1
                i += 1

                # Swapping element at i with element at j
                data[i], data[j] = data[j], data[i]

        # Swap the pivot element with
        # e greater element specified by i
        data[i + 1], data[high] = data[high], data[i + 1]

        # Return the position from where partition is done
        return i + 1
