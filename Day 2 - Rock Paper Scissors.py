"""Day 2: Rock Paper Scissors"""
import time

"""Each score has 2 parts: 
a) game_score = 0 (loss), 3 (draw) and 6 (win).
b) choice_score = 1 (rock), 2 (paper) and 3 (scissors)
Each score has two chars, the first being what the elf chose, the second being
what you chose. A an X are Rock, B and Y are Paper, C and Z are Scissors.
Rules: Rock beats Scissors, Scissors beats Paper, Paper beats Rock."""
scores: dict[str, int] = \
    {"A X": 3 + 1,  # Rock A = Rock X
     "A Y": 6 + 2,  # Paper Y beats Rock A
     "A Z": 0 + 3,  # Rock A beats Scissors Z
     "B X": 0 + 1,  # Paper B beats Rock X => 0
     "B Y": 3 + 2,  # Paper B = Paper Y
     "B Z": 6 + 3,  # Scissors Z beats Paper B
     "C X": 6 + 1,  # Rock X beats Scissors C
     "C Y": 0 + 2,  # Scissors C beats Paper Y
     "C Z": 3 + 3  # Scissors C = Scissors Z
     }

"""Each key has two chars, separated by a space:
- the first is the elf's choice (A = Rock, B = Paper, C = Scissors)
- the second is an instruction for you (X = you must loose, Y = you must draw,
  Z = you must win.
Each value has two chars, separated by a space:
- the first is the elf's choice (same as in the key)
- the second us your choice such that you comply with the instruction in the 
  key (X = Rock, Y = Paper, Z = Scissors)."""
choices: dict[str, str] = \
    {"A X": "A Z",  # Must loose from Rock, so must choose Scissors Z
     "A Y": "A X",  # Must draw with Rock A, so must choose Rock X
     "A Z": "A Y",  # Must win from Rock A, so must choose Paper Y
     "B X": "B X",  # Must loose from Paper B, so must choose Rock X
     "B Y": "B Y",  # Must draw with Paper B, so must choose Paper Y
     "B Z": "B Z",  # Must win from Paper B, so must choose Scissors Z
     "C X": "C Y",  # Must loose from Scissors C, so must choose Peper Y
     "C Y": "C Z",  # Must draw with Scissors C, so must choose Scissors Z
     "C Z": "C X",  # Must win from Scissors C, so must choose Rock X
     }


def get_scores():
    """Return scores for both parts (strategies)."""

    total_score_1 = total_score_2 = 0

    with open("input_files/day2.txt") as file:
        for line in file.readlines():
            line = line[:3]
            total_score_1 += scores[line]
            total_score_2 += scores[choices[line]]

    return total_score_1, total_score_2


def main():
    """Solve the problems."""

    part_1 = "What would your total score be if everything goes exactly " \
             "according to your strategy guide?"
    part_2 = "Following the Elf's instructions for the second column, what " \
             "would your total score be if everything goes exactly " \
             "according to your strategy guide?"

    start = time.perf_counter_ns()

    strategy_scores = get_scores()

    solution_1 = strategy_scores[0]
    solution_2 = strategy_scores[1]

    stop = time.perf_counter_ns()

    assert solution_1 == 12772
    print(f"Day 2 part 1: {part_1} {solution_1}")

    assert solution_2 == 11618
    print(f"Day 2 part 2: {part_2} {solution_2}")

    print(f"Day 2 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
