"""Day 2: Rock Paper Scissors"""
import time

"""The play_to_score dict:
1) Each key has two chars, separated by a space char. The first char is the 
   elf's choice, the second your choice. A an X are Rock, B and Y are Paper, C 
   and Z are Scissors.
2) Each value is a total score, being the sum of 2 parts: 
   a) game score: 0 (you loose), 3 (draw) or 6 (you win).
   b) choice score: 1 (you chose Rock), 2 (you chose Paper) and 3 (you chose 
      Scissors).
Rules: Rock beats Scissors, Scissors beat Paper, Paper beats Rock."""

play_to_score = \
    {"A X": 3 + 1,  # Elf's Rock A vs. your Rock X: Draw
     "A Y": 6 + 2,  # Elf's Rock A vs. your Paper Y: You win
     "A Z": 0 + 3,  # Elf's Rock A vs. your Scissors Z: You lose
     "B X": 0 + 1,  # Elf's Paper B vs. your Rock X: You lose
     "B Y": 3 + 2,  # Elf's Paper B vs. your Paper Y: Draw
     "B Z": 6 + 3,  # Elf's Paper B vs. your Scissors Z: You win
     "C X": 6 + 1,  # Elf's Scissors C vs. your Rock X: You win
     "C Y": 0 + 2,  # Elf's Scissors C vs. your Paper Y: You lose
     "C Z": 3 + 3   # Elf's Scissors C vs. your Scissors Z: Draw
     }

"""The result_to_play dict:
1) Each key has two chars, separated by a space char. The first char is the 
   elf's choice, the second is the desired result: X = you must loose, Y = you 
   must draw, Z = you must win.
2) Each value has two chars, separated by a space:
   - the first is the elf's choice (same as in the key)
   - the second is your choice (X = Rock, Y = Paper, Z = Scissors) such that 
     the desired result (as specified in the second char of the key) is 
     realized."""

result_to_play = \
    {"A X": "A Z",  # Must loose. Elf's Rock A vs. your Scissors Z: you loose
     "A Y": "A X",  # Must draw. Elf's Rock A vs. your Rock X: draw
     "A Z": "A Y",  # Must win. Elf's Rock A vs. your Paper Y: you win
     "B X": "B X",  # Must loose. Elf's Paper B vs. your Rock X: you loose
     "B Y": "B Y",  # Must draw. Elf's Paper B vs. your Paper Y: draw
     "B Z": "B Z",  # Must win: Elf's Paper B vs. your Scissors Z: you win
     "C X": "C Y",  # Must loose: Els Scissors C vs. your Peper Y: you loose
     "C Y": "C Z",  # Must draw: Elf's Scissors C vs. your Scissors Z: draw
     "C Z": "C X",  # Must win: Elf's Scissors C vs. your Rock X: you win.
     }


def get_scores() -> tuple[int, int]:
    """Return play_to_score for both parts (strategies)."""

    with open("input_files/day2.txt") as input_file:
        lines = input_file.read().splitlines()

    total_score_1 = sum(play_to_score[line] for line in lines)
    total_score_2 = sum(play_to_score[result_to_play[line]] for line in lines)

    return total_score_1, total_score_2


def main() -> None:
    """Solve the problems."""

    part_1 = "What would your total score be if everything goes exactly " \
             "according to your strategy guide?"
    part_2 = "Following the Elf's instructions for the second column, what " \
             "would your total score be if everything goes exactly " \
             "according to your strategy guide?"

    start = time.perf_counter_ns()

    solution_1, solution_2 = get_scores()

    stop = time.perf_counter_ns()

    assert solution_1 == 12772
    print(f"Day 2 part 1: {part_1} {solution_1}")

    assert solution_2 == 11618
    print(f"Day 2 part 2: {part_2} {solution_2}")

    print(f"Day 2 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
