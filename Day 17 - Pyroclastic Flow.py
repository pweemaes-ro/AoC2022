"""Try 3..."""

colors = '⚪🟢🔴'


class JetStream:
	def __init__(self, jet_file: str):
		self.__jets = open(jet_file).readline()[:-1]
		self.__length = len(self.__jets)
		self.__offset = 0
	
	def __iter__(self, item):
		return self
	
	def __next__(self) -> str:
		jet_char = self.__jets[self.__offset]
		self.__offset = (self.__offset + 1) % self.__length
		return jet_char


def print_pf(pf: list[int]) -> None:
	"""Print the field. Uses ⚪ for spaces, 🟢 for rocks."""
	
	row_nr = len(pf) - 1
	for r in pf[::-1]:
		print(f"{row_nr:4d}: {''.join(colors[int(c)] for c in f'{r:07b}')}")
		row_nr -= 1


def has_overlap(mask_rows: list[int], field_rows: list[int]) -> bool:
	"""Return True if any row in mask_rows overlaps with its corresponding row
	in field_rows, else False."""
	
	return any(i & j for i, j in zip(mask_rows, field_rows))


def msb_set(n: int) -> bool:
	"""Return True if bit 6 (zero-based!) is set, else False. This is called
	msb since we work with 7 bits (the width of the field's rows)."""
	
	return 64 & n == 64


def lsb_set(n: int) -> bool:
	"""Return True if bit 0 is set, else False."""
	
	return 1 & n == 1


def can_move_right(mask: list[int], pf_rows: list[int]) -> bool:
	return (not any(lsb_set(n) for n in mask)) and \
		(not has_overlap(shift_right(mask), pf_rows))


def can_move_left(mask: list[int], pf_rows: list[int]) -> bool:
	return (not any(msb_set(n) for n in mask)) and \
		(not has_overlap(shift_left(mask), pf_rows))


def shift_right(rows: list[int]) -> list[int]:
	return [i >> 1 for i in rows]


def shift_left(mask_rows: list[int]) -> list[int]:
	return [i << 1 for i in mask_rows]


def can_move_down(mask_rows: list[int], pf_rows: list[int]):
	return not has_overlap(mask_rows, pf_rows)


def process_jet(jet: str, mask_rows: list[int], pf_rows: list[int]) \
		-> list[int]:
	if jet == ">":
		if can_move_right(mask_rows, pf_rows):
			# print("Jet of gas pushes rock right")
			return shift_right(mask_rows)
	# else:
	# 	print("Jet of gas pushes rock right, but nothing happens:")
	else:
		if can_move_left(mask_rows, pf_rows):
			# print("Jet of gas pushes rock left")
			return shift_left(mask_rows)
	# else:
	# 	print("Jet of gas pushes rock left, but nothing happens:")
	
	return mask_rows


def prepare_playing_field(pf: list[int], mask_rows: list[int]) \
		-> tuple[int, int, list[int]]:
	y_min = len(pf) - 1
	while pf[y_min] == 0:
		y_min -= 1
		del pf[-1]
	
	pf.extend([0 for _ in range(3)])
	nr_mask_rows = len(mask_rows)
	
	# Add empty rows for new mask
	pf.extend([0 for _ in range(nr_mask_rows)])
	
	y_max = y_min + 3 + nr_mask_rows
	
	return y_min, y_max, pf


def main() -> None:
	pf = [127]
	masks = [[30], [8, 28, 8], [28, 4, 4], [16, 16, 16, 16], [24, 24]]
	jet_stream = JetStream("input_files/day17.txt")
	
	for n in range(2022):
		mask_rows = masks[n % 5]
		nr_mask_rows = len(mask_rows)
		
		# Remove rows from top until non-empty row (at max height)
		y_min, y_max, pf = prepare_playing_field(pf, mask_rows)
		
		# Get pf rows against which we do initial moves to left or right
		# Do moves left and right
		while True:
			left_right_window = pf[y_max + 1 - nr_mask_rows: y_max + 1]
			mask_rows = process_jet(next(jet_stream), mask_rows,
									left_right_window
									)
			down_window = pf[y_max - nr_mask_rows: y_max]
			
			if has_overlap(mask_rows, down_window):
				break
			else:
				y_min -= 1
				y_max -= 1
		
		# Integrate mask in playing field
		for i in range(nr_mask_rows):
			pf[y_max - i] = mask_rows[nr_mask_rows - 1 - i] | pf[y_max - i]
		
		while not pf[-1]:
			del pf[-1]
	
	print(len(pf) - 1)


if __name__ == "__main__":
	main()
