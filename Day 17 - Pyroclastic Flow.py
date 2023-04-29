"""Try 3..."""

colors = '⚪🟢🔴'


class JetStream:
	"""We use a class to handle the retrieval of jets and the positioning in
	the stream, since this is very much dealing with state."""
	
	def __init__(self, jet_file: str):
		with open(jet_file) as jet_stream:
			self.__jets = jet_stream.readline()[:-1]
		self.__length = len(self.__jets)
		self.__offset = 0
	
	def __iter__(self, item):
		return self
	
	def __next__(self) -> str:
		jet_char = self.__jets[self.__offset]
		self.__offset = (self.__offset + 1) % self.__length
		return jet_char
	
	@property
	def offset(self) -> int:
		return self.__offset


def print_pf(pf: list[int]) -> None:
	"""Print the field. Uses ⚪ for spaces, 🟢 for rocks."""
	
	# Todo: Function can be removed when code complete
	row_nr = len(pf) - 1
	for r in pf[::-1]:
		print(f"{row_nr:4d}: {''.join(colors[int(c)] for c in f'{r:07b}')}")
		# print(r)
		row_nr -= 1


def rows_overlap(mask_rows: list[int], field_rows: list[int]) -> bool:
	"""Return True if any row in mask_rows overlaps with its corresponding row
	in field_rows, else False."""
	
	return any(i & j for i, j in zip(mask_rows, field_rows))


def bit_set(n: int, bit_nr: int) -> bool:
	"""Return True if bit at (zero based) offset bit_nr is set in n, else
	return False."""
	
	bit_value = 2 ** bit_nr
	return bit_value & n == bit_value


def can_shift_right(mask_rows: list[int], playfield_rows: list[int]) -> bool:
	"""Return True if it is ok to shift mask_rows to the right, else return
	False."""
	
	return (not any(bit_set(n, bit_nr=0) for n in mask_rows)) and \
		(not rows_overlap(shift_right(mask_rows), playfield_rows))


def can_shift_left(mask_rows: list[int], playfield_rows: list[int]) -> bool:
	"""Return True if it is ok to shift mask_rows to the left, else return
	False."""
	
	return (not any(bit_set(n, bit_nr=6) for n in mask_rows)) and \
		(not rows_overlap(shift_left(mask_rows), playfield_rows))


# def can_move_down(mask_rows: list[int], playfield_rows: list[int]):
# 	"""Return True if it is ok to move mask_rows down, else return
# 	False. Notice that 'playfield_rows' are the rows on the playfield where
# 	the mask would end up after moving down."""
# 	return not rows_overlap(mask_rows, playfield_rows)


def shift_right(mask_rows: list[int]) -> list[int]:
	return [i >> 1 for i in mask_rows]


def shift_left(mask_rows: list[int]) -> list[int]:
	return [i << 1 for i in mask_rows]


def process_jet(direction: str, mask_rows: list[int],
				playfield_rows: list[int]) -> list[int]:
	"""Shifts the mask rows in the specified direction if possible. Returns the
	(possibly unchanged) mask rows."""
	
	if direction == ">":
		if can_shift_right(mask_rows, playfield_rows):
			return shift_right(mask_rows)
	else:
		if can_shift_left(mask_rows, playfield_rows):
			return shift_left(mask_rows)
	
	return mask_rows


def prepare_playing_field(pf: list[int], mask_rows: list[int]) \
		-> tuple[int, int, list[int]]:
	"""Prepares the next drop by putting three empty lines above the highest
	column in the playing field"""
	
	# Why remove rows first and then add more rows?
	# y_min is the lowest relevant row nr (the higest row containing rock)
	y_min = len(pf) - 1
	while not pf[y_min]:
		y_min -= 1
	
	nr_mask_rows = len(mask_rows)
	
	# Add empty rows for new mask
	pf.extend([0 for _ in range(nr_mask_rows)])
	
	# y_max is the highest
	y_max = y_min + 3 + nr_mask_rows
	
	return y_min, y_max, pf


# y_min = len(pf) - 1
# while pf[y_min] == 0:
# 	y_min -= 1
# 	del pf[-1]
#
# pf.extend([0 for _ in range(3)])
# nr_mask_rows = len(mask_rows)
#
# # Add empty rows for new mask
# pf.extend([0 for _ in range(nr_mask_rows)])
#
# y_max = y_min + 3 + nr_mask_rows
#
# return y_min, y_max, pf


# def get_repeat_key(pf: list[int]) -> int:
# 	row_nr = -1
# 	key_as_list = [0] * 7
# 	while 0 not in key_as_list:
# 		pf_row_value = pf[row_nr]


def main() -> None:
	pf = [127]
	masks = [[30], [8, 28, 8], [28, 4, 4], [16, 16, 16, 16], [24, 24]]
	use_test_data = False
	if use_test_data:
		file_name = "input_files/day17t1.txt"
		print("Using test data")
		expected_1 = 3068
		expected_2 = 1_514_285_714_288
	else:
		file_name = "input_files/day17.txt"
		print("Using real input data")
		expected_1 = 3119
		expected_2 = None
	jet_stream = JetStream(file_name)
	
	# repeat_info: dict[int, tuple[int, int]] = dict()
	for n in range(2022):
		mask_rows = masks[n % 5]
		nr_mask_rows = len(mask_rows)
		
		# Remove rows from top until non-empty row (at max height)
		y_min, y_max, pf = prepare_playing_field(pf, mask_rows)
		print(f"{y_min=}, {y_max=}, {len(mask_rows)=}, {len(pf)=}", end='')
		print(f"lrw start: pf[{y_max + 1 - nr_mask_rows}:{y_max + 1}]")
		# Get pf rows against which we do initial moves to left or right
		# Do moves left and right
		while True:
			left_right_window = pf[y_max + 1 - nr_mask_rows: y_max + 1]
			mask_rows = process_jet(next(jet_stream), mask_rows,
									left_right_window
									)
			down_window = pf[y_max - nr_mask_rows: y_max]
			
			if rows_overlap(mask_rows, down_window):
				break
			else:
				y_min -= 1
				y_max -= 1
		
		# Integrate mask in playing field
		for i in range(nr_mask_rows):
			pf[y_max - i] = mask_rows[nr_mask_rows - 1 - i] | pf[y_max - i]
		
		while not pf[-1]:
			del pf[-1]
	
	# repeat_info[n] = (len(pf) - 1, jet_stream.offset)
	# repeat_key = get_repeat_key(pf)
	# if repeat_mask := repeat_info.get(repeat_key, None):
	# 	if repeat_mask == mask_rows:
	# 		print(f"repeat found: {n = }")
	# else:
	# 	repeat_info[repeat_key] = mask_rows
	solution_1 = len(pf) - 1  # 3068 for test input, 3119 for real input,
	assert solution_1 == expected_1
	print(solution_1)


# print_pf(pf)
# for n, (length, jets) in repeat_info.items():
# 	print(f"{n}, {length}, {jets}")


if __name__ == "__main__":
	main()
