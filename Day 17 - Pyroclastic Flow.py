"""Try 3..."""
from collections.abc import Iterator
from typing import Final

from AoCLib.IntsAndBits import bit_set


class JetStream:
	"""We use a class to handle the retrieval of jets and the positioning in
	the stream, since this is very much dealing with state."""
	
	def __init__(self, jet_file: str):
		
		with open(jet_file) as jet_stream:
			self.__jets = jet_stream.readline()[:-1]
		self.__length = len(self.__jets)
		self.__offset = 0
	
	def __iter__(self) -> Iterator[str]:
		
		return self
	
	def __next__(self) -> str:
		
		jet_char = self.__jets[self.__offset]
		self.__offset = (self.__offset + 1) % self.__length
		return jet_char
	
	@property
	def current_offset(self) -> int:
		"""Return the current offset in the jet stream."""
		
		return self.__offset


class PlayField(list[int]):
	"""Representation of the play field (rows of rock), and functionality to
	drop - in a tetris-like manner - rocks. The left/right movements of falling
	rocks are controlled by the jets."""
	
	_colors: Final = '⚪🟢'
	
	def __init__(self, jet_stream: JetStream, rock_shapes: list[list[int]]) \
		-> None:
		
		super().__init__([127])		# First row is full, so falling through...
		self._jet_stream = jet_stream
		self._rock_shapes = rock_shapes
		
		self._cycle_start_offset: int = 0
		self._cycle_length = 0
	
	@staticmethod
	def _can_move_to_right(rock_rows: list[int], play_field_rows: list[int]) \
		-> bool:
		"""Return True if it is ok to shift rock_rows to the right, else return
		False."""
		
		# We can move the rock rows to the right if:
		# a) All rock rows have bit 6 equal to 0, AND
		# b) No bits in the play field overlap with where the rock would go
		#    after shifting to the right.
		return (not any(bit_set(n, bit_nr=0) for n in rock_rows)) and \
			(not rows_overlap([i >> 1 for i in rock_rows], play_field_rows))
	
	@staticmethod
	def _can_move_to_left(rock_rows: list[int], play_field_rows: list[int]) \
		-> bool:
		"""Return True if it is ok to shift rock_rows to the left, else return
		False."""
		
		# We can move the rock rows to the left if:
		# a) All rock rows have bit 6 equal to 0, AND
		# b) No bits in the play field overlap with where the rock would go
		#    after shifting to the right.
		return (not any(bit_set(n, bit_nr=6) for n in rock_rows)) and \
			(not rows_overlap([i << 1 for i in rock_rows], play_field_rows))
	
	def try_move_sideways(
		self, rock_rows: list[int],
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
	
	def analyse(self) -> None:
		"""Should analyse and determine all essential data"""
	
		pass
		
	def get_height_after_drops(self, nr_drops: int) -> int:
		"""Returns the height after the specified nr of rocks has been dropped.
		"""
		
		if nr_drops > 2022:
			print(f"{nr_drops = } too high...")
			return -1
		
		for n in range(nr_drops):
			self._drop(n)
		return self.height
	
	def _drop(self, n: int) -> None:
		rock_shape = self._rock_shapes[n % 5]
		rock_height = len(rock_shape)
		
		# Make sure here are sufficient empty rows.
		while not self[-1]:
			del self[-1]
		self.extend([0] * 4)
		
		rock_start_row = len(self) - 1
		
		while True:
			# Try to move one position to the left or right
			sideways_window = self[rock_start_row:rock_start_row + rock_height]
			rock_shape = self.try_move_sideways(rock_shape, sideways_window)
			
			down_window = self[rock_start_row - 1:
							   rock_start_row - 1 + rock_height]
			if rows_overlap(rock_shape, down_window):
				break
			else:
				rock_start_row -= 1
		
		for i in range(rock_height):
			self[rock_start_row + i] |= rock_shape[i]
	
	@property
	def height(self) -> int:
		"""Returns the height of the play field (which is not necessarily the
		same as the nr of rows, since there may be empty rows on the top of
		the play field)."""
		
		empty_rows = 0
		
		while not self[-(empty_rows + 1)]:
			empty_rows += 1
		
		return len(self) - 1 - empty_rows
	
	def _prepare_next_drop(self) -> None:
		"""Prepares the next drop by putting four empty lines above the
		highest column in the playing field. Return the offset of the highest
		non-empty row."""
		
		# Remove all empty rows from above
		while not self[-1]:
			del self[-1]
		
		# Add 4 empty rows (4 is the max height of a rock).
		self.extend([0] * 4)
	
	def __str__(self) -> str:
		"""Print the field. Uses ⚪ for spaces, 🟢 for rocks."""
		
		# Todo: Function can be removed when code complete
		return '\n'.join(f"{row_nr:4d}: "
						 f"{''.join(self._colors[int(c)] for c in f'{r:07b}')}"
						 for row_nr, r in enumerate(self[::-1]))


def rows_overlap(rock_rows: list[int], field_rows: list[int]) -> bool:
	"""Return True if any row in rock_rows overlaps with its corresponding row
	in field_rows, else False."""
	
	return any(i & j for i, j in zip(rock_rows, field_rows))


def main() -> None:
	"""Yeah!"""
	
	use_test_data = True
	
	if use_test_data:
		file_name = "input_files/day17t1.txt"
		print("Using test data")
		expected_1 = 3068
		# expected_2 = 1_514_285_714_288
	else:
		file_name = "input_files/day17.txt"
		print("Using real input data")
		expected_1 = 3119
		# expected_2 = None
	
	jet_stream = JetStream(file_name)
	rock_shapes = [[30], [8, 28, 8], [28, 4, 4], [16, 16, 16, 16], [24, 24]]
	pf = PlayField(jet_stream, rock_shapes)
	
	solution_1 = pf.get_height_after_drops(2022)  # 3068 for test input, 3119 for
	# real input,
	# solution_2 = pf.get_height_after_drops(1_000_000_000_000)
	print(solution_1)
	assert solution_1 == expected_1


if __name__ == "__main__":
	main()
	exit(0)
