"""Day 17 - Pyroclastic Flow"""
import operator
import time
from collections.abc import Iterator
from typing import Callable, TypeAlias

from AoCLib.IntsAndBits import bit_set

Rock: TypeAlias = list[int]
RowOffset: TypeAlias = int


class JetStream:
	"""A class to handle retrieval of jets and positioning in the stream."""
	
	def __init__(self, jet_file: str):
		with open(jet_file) as jet_stream:
			self.__jets = jet_stream.readline()[:-1]
		self._length = len(self.__jets)
		self._offset = 0
		self._jets_yielded = 0
	
	def __iter__(self) -> Iterator[str]:
		"""The JetStream is an iterator itself..."""
		
		return self
	
	def __next__(self) -> str:
		"""Return the next char from the jetstream."""
		
		jet_char = self.__jets[self._offset]
		self._offset = (self._offset + 1) % self._length
		self._jets_yielded += 1
		return jet_char

	def __len__(self) -> int:
		return self._length
	
	@property
	def jets_yielded(self) -> int:
		"""Return the nr of jets processed since the last reset."""
		
		return self._jets_yielded


class PlayField(list[int]):
	"""Representation of the play field (rows of rock), and functionality to
	drop - in a tetris-like manner - rocks. The left/right movements of falling
	rocks are controlled by the jets."""
	
	def __init__(self, jet_stream: JetStream, rocks: list[Rock]) \
		-> None:
		
		super().__init__([127])  # First row is full, so falling through...
		self._jet_stream = jet_stream
		self._rocks = rocks
		self._rocks_dropped = 0
		self._d2h: dict[int, int] = dict()  # nr dropped -> post drops height
		self._drops_before_cycles = 0   # nr of rocks dropped before 1st cycle
		self._cycle_drops = 0           # nr of rocks dropped in one cycle
		self._delta_height_before_cycles = 0  # height reached before 1st cycle
		self._cycle_height = 0                # delta height of one cycle
		self._set_cycle_info()

	@staticmethod
	def _all_leftmost_bit_cleared(rock: Rock) -> bool:
		"""Return True if rock values have leftmost bit cleared, else False."""

		return not any(bit_set(n, 6) for n in rock)

	@staticmethod
	def _all_rightmost_bit_cleared(rock: Rock) -> bool:
		"""Return True if rock values have rightmost bit cleared, else False."""

		return not any(bit_set(n, 0) for n in rock)
	
	def _can_move_to_left(self, rock: Rock, play_field: list[int]) -> bool:
		"""Return True if rock_rows can shift to the left, else return
		False."""
		
		return self._all_leftmost_bit_cleared(rock) and \
			not self._rows_overlap(self._shifted_left(rock), play_field)
	
	def _can_move_to_right(self, rock: Rock, play_field: list[int]) -> bool:
		"""Return True if rock_rows can be shifted to the right, else return
		False."""
		
		return self._all_rightmost_bit_cleared(rock) and \
			not self._rows_overlap(self._shifted_right(rock), play_field)
	
	@staticmethod
	def _shifted_right(rock: Rock) -> Rock:
		"""Return (new) right shifted rock."""
		
		return [i >> 1 for i in rock]
	
	@staticmethod
	def _shifted_left(rock: Rock) -> Rock:
		"""Return (new) left shifted rock."""
		
		return [i << 1 for i in rock]
	
	def _try_move_down(self, rock: Rock, rock_start_offset: int) -> bool:
		"""Return True if rock can move down one unit, else False."""
		
		destination = self[rock_start_offset - 1:
		                   rock_start_offset - 1 + len(rock)]
		
		# We can move down if there is no overlap between the rock when
		# 'projected' on its destination rows in the playing field.
		return not self._rows_overlap(rock, destination)
	
	def _try_move_sideways(self, rock: Rock, rock_start_offset: int) -> Rock:
		"""Shifts the rock in the specified direction if possible. Returns the
		(shifted or unchanged) rock."""
		
		destination = self[rock_start_offset: rock_start_offset + len(rock)]
		
		direction = next(self._jet_stream)
		
		if direction == ">":
			if self._can_move_to_right(rock, destination):
				return self._shifted_right(rock)
		else:
			if self._can_move_to_left(rock, destination):
				return self._shifted_left(rock)
		
		# If move sideways was not possible, return unchanged rock rows!
		return rock
	
	def _put_on_playfield(self, rock: Rock, rock_start_offset: int) -> None:
		"""Puts the rock on the playing field and then stores the height so we
		can re-use it during cycle-detection!"""
		
		for i in range(len(rock)):
			self[rock_start_offset + i] |= rock[i]
		
		self._d2h[self._rocks_dropped] = self._height
		
	@property
	def _jets_yielded(self) -> int:
		"""Return the nr of jets yielded so far."""
		
		return self._jet_stream.jets_yielded
	
	@property
	def _height(self) -> int:
		"""Return the height of the play field (which is not necessarily the
		same as the nr of rows, since there may be empty rows on the top of
		the play field)."""
		
		empty_rows = 0
		while not self[- (empty_rows + 1)]:
			empty_rows += 1
		
		return len(self) - empty_rows - 1
	
	def _prepare_drop(self) -> tuple[Rock, int]:
		"""Return the rock to drop and the row nr of the rock's bottom row."""
		
		rock = self._rocks[self._rocks_dropped % 5]
		self._rocks_dropped += 1

		# Make sure there are exactly 4 (the largest height of all blocks)
		# empty top rows on the playing field.
		while not self[-1]:
			del self[-1]
		self.extend([0] * 4)
		
		return rock, len(self) - 1
	
	def _drop_next_rock(self) -> None:
		"""Drop a rock."""

		rock, rock_start_offset = self._prepare_drop()
		
		while True:
			# Try to move one position to the left or right
			rock = self._try_move_sideways(rock, rock_start_offset)
			
			# Try to move one position down. Stop if it failed.
			if self._try_move_down(rock, rock_start_offset):
				rock_start_offset -= 1
			else:
				break
		
		self._put_on_playfield(rock, rock_start_offset)
	
	def _drop_until_jet_offset(self,
	                           jet_offset: int,
	                           cmp: Callable[[int, int], bool]) -> int:
		"""Drop rocks until compare of processed jets and jet_offset is True.
		Returns nr of drops executed."""
		
		drops_at_start = self._rocks_dropped
		while not cmp(self._jets_yielded, jet_offset):
			self._drop_next_rock()
			
		return self._rocks_dropped - drops_at_start
	
	def _set_cycle_info(self) -> None:
		"""Set all relevent cycle data."""
		
		jets_per_cycle = len(self._jet_stream) * len(self._rocks)
		
		# The only invariant is the nr of jets for each cycle. The nr of rocks
		# dropped before and in a cycle depends on where earlier rocks came to
		# rest. So irst we drop rocks until we are sure we are INSIDE a cycle,
		# that is, we have processed AT LEAST the the invariant nr of jets.
		# This gives the nr of drops and the height just before the first cycle
		# starts.
		
		self._drops_before_cycles = \
			self._drop_until_jet_offset(jets_per_cycle, operator.ge)
		self._delta_height_before_cycles = self._d2h[self._drops_before_cycles]

		# Now we drop until we have processed an additional jets_per_cycle.
		# This gives the nr of drops in eaach cycle and the increase in height
		# of each cycle.
		self._cycle_drops = \
			self._drop_until_jet_offset(self._jets_yielded
			                            + jets_per_cycle, operator.eq)
		self._cycle_height = self._height - self._delta_height_before_cycles
		
	def get_tallest_tower(self, nr_drops: int) -> int:
		"""Return the height of the tower of rocks after nr_drops rocks have
		stopped falling. This is determined by calculation, based on analysis
		of cyclicity, not by simmulating all drops. (Only the drops required to
		get to the beginning of the 2nd cycle are actually simulated, see
		self._set_cycle_info method)."""
		
		nr_cycles, drops_after_cycles = \
			divmod(nr_drops - self._drops_before_cycles, self._cycle_drops)

		delta_height_in_cycles = nr_cycles * self._cycle_height

		delta_height_after_cycles = \
			self._d2h[self._drops_before_cycles + drops_after_cycles] \
			- self._delta_height_before_cycles
		
		return self._delta_height_before_cycles \
			+ delta_height_in_cycles \
			+ delta_height_after_cycles
	
	@staticmethod
	def _rows_overlap(rock: Rock, play_field: list[int]) -> bool:
		"""Return True if any row in rock_rows overlaps with its corresponding
		row in field_rows, else False."""
		
		return any(i & j for i, j in zip(rock, play_field))


def main() -> None:
	"""Solve the puzzle."""
	
	part_1 = "How many units tall will the tower of rocks be after 2022 " \
	         "rocks have stopped falling?"
	part_2 = "How tall will the tower be after 1000000000000 rocks have " \
	         "stopped?"
	
	start = time.perf_counter_ns()
	
	jet_stream = JetStream("input_files/day17.txt")
	rocks: list[Rock] = [
		[30],
		# rock shape:
		# 🟢🟢🟢🟢
		
		[8, 28, 8],
		# rock shape:
		# ⚪🟢⚪
		# 🟢🟢🟢
		# ⚪🟢⚪
		
		[28, 4, 4],
		# rock shape:
		# ⚪⚪🟢
		# ⚪⚪🟢
		# 🟢🟢🟢
		
		[16, 16, 16, 16],
		# rock shape:
		# 🟢
		# 🟢
		# 🟢
		# 🟢
		
		[24, 24]
		# rock shape:
		# 🟢🟢
		# 🟢🟢
	]
	
	play_field = PlayField(jet_stream, rocks)
	
	solution_1 = play_field.get_tallest_tower(2022)
	solution_2 = play_field.get_tallest_tower(1_000_000_000_000)
	
	stop = time.perf_counter_ns()
	
	assert solution_1 == 3119
	print(f"Day 17 part 1: {part_1} {solution_1:_}")
	
	assert solution_2 == 1_536_994_219_669
	print(f"Day 17 part 2: {part_2} {solution_2:_}")
	
	print(f"Day 17 took {(stop - start) * 10 ** -6:_.3f} ms")


if __name__ == "__main__":
	main()
