"""Try 3..."""
import time
from collections.abc import Iterator
from typing import Final

from AoCLib.IntsAndBits import bit_set


class JetStream:
	"""A class to handle retrieval of jets and positioning in the stream."""
	
	def __init__(self, jet_file: str):
		
		with open(jet_file) as jet_stream:
			self.__jets = jet_stream.readline()[:-1]
		self._length = len(self.__jets)
		self.__offset = 0
		self._jets_yielded = 0
		
	def __iter__(self) -> Iterator[str]:
		"""The JetStream is an iterator itself..."""
		
		return self
	
	def __next__(self) -> str:
		"""Return the next char from the jetstream."""
		
		jet_char = self.__jets[self.__offset]
		self.__offset = (self.__offset + 1) % self._length
		self._jets_yielded += 1
		return jet_char
	
	@property
	def length(self) -> int:
		"""Returns the length of the jetstream."""
		
		return self._length

	@property
	def jets_yielded(self) -> int:
		"""Return the nr of jets processed since the last reset."""
		
		return self._jets_yielded

		
class PlayField(list[int]):
	"""Representation of the play field (rows of rock), and functionality to
	drop - in a tetris-like manner - rocks. The left/right movements of falling
	rocks are controlled by the jets."""
	
	_colors: Final = '⚪🟢'
	
	def __init__(self, jet_stream: JetStream, rock_shapes: list[list[int]]) \
		-> None:
		
		super().__init__([127])  # First row is full, so falling through...
		self._jet_stream = jet_stream
		self._rock_shapes = rock_shapes
		self._rocks_dropped = 0
		# There are only five rock-shapes and only x = a finite nr of jet chars, so
		# there is a cycle that takes exactly 5 * x jet chars.
		self._jets_per_cycle = self._jet_stream.length * len(self._rock_shapes)
		self._delta_height_per_cycle = 0
		self._drops_at_start_of_first_cycle = 0
		self._drops_per_cycle = 0
		self._cycle_found = False
		self._drops_to_heights: dict[int, int] = dict()

	def _can_move_to_right(self,
						   rock_rows: list[int],
						   play_field_rows: list[int]) -> bool:
		"""Return True if rock_rows can be shifted to the right, else return
		False."""
		
		# We can move the rock rows to the right if:
		# a) All rock rows have bit 0 equal to 0 (not already against the right
		#    edge of the playing field), AND
		# b) No bits in the play field overlap with where the rock would go
		#    after shifting to the right.
		return (not any(bit_set(n, bit_nr=0) for n in rock_rows)) and \
			(not self.rows_overlap([i >> 1 for i in rock_rows], play_field_rows))
	
	def _can_move_to_left(self,
						  rock_rows: list[int],
						  play_field_rows: list[int]) -> bool:
		"""Return True if rock_rows can shift to the left, else return False."""
		
		# We can move the rock rows to the left if:
		# a) All rock rows have bit 6 equal to 0 (not already against the left
		#    edge of the playing field), AND
		# b) No bits in the play field overlap with where the rock would go
		#    after shifting to the left.
		return (not any(bit_set(n, bit_nr=6) for n in rock_rows)) and \
			(not self.rows_overlap([i << 1 for i in rock_rows], play_field_rows))
	
	def try_move_sideways(self, rock_rows: list[int],
						  play_field_rows: list[int]) -> list[int]:
		"""Shifts the rock rows in the specified direction if possible. Returns
		the (possibly unchanged) rock rows."""
		
		direction = next(self._jet_stream)
		
		if direction == ">":
			if self._can_move_to_right(rock_rows, play_field_rows):
				return [i >> 1 for i in rock_rows]
		else:
			if self._can_move_to_left(rock_rows, play_field_rows):
				return [i << 1 for i in rock_rows]
		
		return rock_rows
	
	@property
	def height(self) -> int:
		"""Return the height of the play field (which is not necessarily the
		same as the nr of rows, since there may be empty rows on the top of
		the play field)."""

		empty_rows = 0
		while not self[- (empty_rows + 1)]:
			empty_rows += 1
			
		return len(self) - empty_rows - 1

	def _drop_next_rock(self) -> None:
		"""Drop a rock."""
		
		rock_shape = self._rock_shapes[self._rocks_dropped % 5]
		self._rocks_dropped += 1
		rock_height = len(rock_shape)
		
		# Make sure there are sufficient empty rows.
		while not self[-1]:
			del self[-1]
		self.extend([0] * 4)  # 4 is the largest height of all blocks!
		
		rock_bottom_row = len(self) - 1
		
		while True:
			# Try to move one position to the left or right
			sideways_window = self[
							  rock_bottom_row: rock_bottom_row + rock_height]
			rock_shape = self.try_move_sideways(rock_shape, sideways_window)
			
			down_window = self[rock_bottom_row - 1:
							   rock_bottom_row - 1 + rock_height]
			
			# We can move down if there is no overlap between the rock_shape
			# when 'projected' on its location after moving down.
			if self.rows_overlap(rock_shape, down_window):
				break
			else:
				rock_bottom_row -= 1
		
		# The rock cannot move down anymore, put it at its location in the
		# playfield.
		for i in range(rock_height):
			self[rock_bottom_row + i] |= rock_shape[i]
		
		self._drops_to_heights[self._rocks_dropped] = self.height
	
	def _find_cycle(self) -> None:

		jet_offset_at_start_of_second_cycle = -1
	
		while True:
			if not self._drops_at_start_of_first_cycle and \
				self._jet_stream.jets_yielded >= self._jets_per_cycle:
				
				self._drops_at_start_of_first_cycle = self._rocks_dropped

				jet_offset_at_start_of_second_cycle = \
					self._jet_stream.jets_yielded + self._jets_per_cycle

				self._drop_next_rock()

			elif self._jet_stream.jets_yielded == \
				jet_offset_at_start_of_second_cycle:

				self._delta_height_per_cycle = \
					self.height - \
					self._drops_to_heights[self._drops_at_start_of_first_cycle]
				self._drops_per_cycle = \
					self._rocks_dropped - \
					self._drops_at_start_of_first_cycle

				break
			
			else:
				self._drop_next_rock()
		
		self._cycle_found = True

	def height_after_drops(self, total_drops: int) -> int:
		"""Return the height after dropping total_drops rocks."""

		if not self._cycle_found:
			self._find_cycle()
		
		nr_cycles, drops_in_lead_out = \
			divmod(total_drops - self._drops_at_start_of_first_cycle,
				self._drops_per_cycle)
		in_cycles_height = nr_cycles * self._delta_height_per_cycle
		
		lead_out_height = \
			self._drops_to_heights[self._drops_at_start_of_first_cycle +
								   drops_in_lead_out] - \
			self._drops_to_heights[self._drops_at_start_of_first_cycle]

		return self._drops_to_heights[self._drops_at_start_of_first_cycle] + \
			in_cycles_height + \
			lead_out_height

	# def __str__(self) -> str:
	# 	"""Print the field. Uses ⚪ for spaces, 🟢 for rocks."""
	#
	# 	return '\n'.join(f"{len(self) - 1 - row_nr:4d}: "
	# 					 f"{''.join(self._colors[int(c)] for c in f'{r:07b}')}"
	# 					 for row_nr, r in enumerate(self[::-1]))

	@staticmethod
	def rows_overlap(rock_rows: list[int], field_rows: list[int]) -> bool:
		"""Return True if any row in rock_rows overlaps with its corresponding row
		in field_rows, else False."""
		
		return any(i & j for i, j in zip(rock_rows, field_rows))


def main() -> None:
	"""Solve the puzzle."""
	
	part_1 = "How many units tall will the tower of rocks be after 2022 " \
	         "rocks have stopped falling?"
	part_2 = "How tall will the tower be after 1000000000000 rocks have " \
	         "stopped?"
	
	# use_test_data = False
	#
	# if use_test_data:
	# 	file_name = "input_files/day17t1.txt"
	# 	expected_1 = 3068
	# 	expected_2 = 1514285714288
	# else:
	# 	file_name = "input_files/day17.txt"
	# 	expected_1 = 3119
	# 	expected_2 = 1536994219669
	
	start = time.perf_counter_ns()
	
	jet_stream = JetStream("input_files/day17.txt")
	rock_shapes = [[30], [8, 28, 8], [28, 4, 4], [16, 16, 16, 16], [24, 24]]
	pf = PlayField(jet_stream, rock_shapes)

	solution_1 = pf.height_after_drops(2022)
	solution_2 = pf.height_after_drops(1_000_000_000_000)
	
	stop = time.perf_counter_ns()
	
	assert solution_1 == 3119
	print(f"Day 17 part 1: {part_1} {solution_1:_}")
	
	assert solution_2 == 1_536_994_219_669
	print(f"Day 17 part 2: {part_2} {solution_2:_}")
	
	print(f"Day 17 took {(stop - start) * 10 ** -6:_.3f} ms")


if __name__ == "__main__":
	main()
