"""Day 10: Cathode Ray Tube."""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from typing import IO, Callable, Any

Registers = list[int]
Params = list[Any]
Executor = Callable[[Registers, Params], Registers]
ClockListenerCallback = Callable[[int, Registers], None]


class Instruction:
    """Instruction class."""

    def __init__(self, name: str, nr_params: int, cycles: int,
                 executor: Executor):
        self._name = name
        self._cycles = cycles
        self._executor = executor
        self._nr_params = nr_params
        self._params: list[Any] = []

    def _params_setter(self, params: Params) -> None:
        """Property getter"""

        self._params = params

    # noinspection PyArgumentEqualDefault
    params = property(None, _params_setter, None,
                      "Set params for next execution")

    @property
    def name(self) -> str:
        """Return the name of the instruction."""

        return self._name

    def execute(self, registers: list[int]) -> list[int]:
        """Execute this instruction (by calling its executor) using the
        params"""

        result = self._executor(registers, self._params)
        self._params = []
        return result

    @property
    def cycles(self) -> int:
        """Return the nr of cycles that execution of this instruction takes."""

        return self._cycles


class ClockSignalListener(ABC):
    """Abstract base class for Clock Listeners."""

    def __init__(self, cpu: CPU):
        """Store the cpu and register yourself with the cpu."""
        self._cpu = cpu
        cpu.register_listener(self, self._callback)

    @abstractmethod
    def _callback(self, cycle_nr: int, registers: list[int]):
        """This must be implemented by concrete classes."""

        pass


class SignalChecker(ClockSignalListener):
    """A concrete Clock Listener."""

    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self._result = 0

    def _callback(self, cycle_nr: int, registers: list[int]):
        """We are interested in cycles 20, 60, 100, 140 etc."""

        if cycle_nr == 20 or ((cycle_nr - 20) % 40) == 0:
            self._result += cycle_nr * registers[0]

    def get_result(self) -> int:
        """Return the current value of the sum of the signal strengths."""

        return self._result


class CRT(ClockSignalListener):
    """A concrete Clock Listener."""

    _lines = 6
    _pix_per_line = 40

    def __init__(self, cpu: CPU):
        super().__init__(cpu)
        self._screen = [" "] * self._lines * self._pix_per_line

    def _callback(self, cycle_nr: int, registers: list[int]):
        """This one is interested in every single cycle!"""

        locations = tuple(i + registers[0] for i in range(-1, 2))
        if ((cycle_nr - 1) % self._pix_per_line) in locations:
            self._screen[cycle_nr - 1] = "█"
        else:
            self._screen[cycle_nr - 1] = " "
        assert True

    def get_result(self) -> str:
        """Return the image on the CRT."""

        screen_to_str = ''.join(self._screen)
        return "\n".join(
            [screen_to_str[i * self._pix_per_line:
                           i * self._pix_per_line + self._pix_per_line]
             for i in range(6)])


class CPU:
    """The CPU."""

    __nr_registers = 1      # Currently only 1 register needed

    def __init__(self, instructions: list[Instruction], instruction_bus: IO):
        self._instructions = {instruction.name: instruction
                              for instruction in instructions}
        self._instruction_bus = instruction_bus
        self._registers = [1 for _ in range(self.__nr_registers)]
        self._cycle_count = 0
        self._listeners: list[tuple[ClockSignalListener, Callable]] = []

    def register_listener(self,
                          listener: ClockSignalListener,
                          callback: ClockListenerCallback):
        """Register the listener and its callback."""

        self._listeners.append((listener, callback))

    def __increment_cycles(self, nr_to_add: int):
        for i in range(nr_to_add):
            self._cycle_count += 1
            for listener, callback in self._listeners:
                callback(self._cycle_count, self._registers)

    def __fetch_instruction(self) -> Instruction | None:
        """Fetch instruction + params from the instruction bus."""

        if not (line := self._instruction_bus.readline()):
            return None

        parts = line[:-1].split()
        instruction_name = parts[0]

        instruction = self._instructions.get(instruction_name, None)
        if not instruction:
            print(f"FATAL ERROR: INVALID/UNKNOWN instruction "
                  f"'{instruction_name}': ABORTING!")
            exit(1)
        instruction.params = parts[1:]
        return instruction

    def start(self):
        """Start fetching and executing instructions until ready."""
        while instruction := self.__fetch_instruction():
            # self.cycles = instruction.cycles
            self.__increment_cycles(instruction.cycles)
            self._registers = instruction.execute(self._registers)


# noinspection PyUnusedLocal
def noop_executor(registers: Registers, params: Params) -> Registers:
    """The executor for the noop instruction (noop = no operation)."""
    return registers


def addx_executor(registers: Registers, params: Params) -> Registers:
    """The executor for the addx instructor (addx = add x to register[0]."""

    registers[0] += int(params[0])
    return registers


def main() -> None:
    """Solve the puzzle"""

    part_1 = "Find the signal strength during the 20th, 60th, 100th, " \
             "140th, 180th, and 220th cycles. What is the sum of these six " \
             "signal strengths?"
    part_2 = "Render the image given by your program. What eight capital " \
             "letters appear on your CRT?"

    start = time.perf_counter_ns()

    with open("input_files/day10.txt") as input_file:
        noop = Instruction(name="noop",
                           cycles=1,
                           nr_params=0,
                           executor=noop_executor)
        addx = Instruction(name="addx",
                           cycles=2,
                           nr_params=1,
                           executor=addx_executor)
        cpu = CPU([noop, addx], input_file)
        signal_strength_device = SignalChecker(cpu)
        crt = CRT(cpu)
        cpu.start()

    solution_1 = signal_strength_device.get_result()
    solution_2 = crt.get_result()

    stop = time.perf_counter_ns()

    assert solution_1 == 14340
    print(f"Day ... part 1: {part_1} {solution_1}")

    capitals = "███   ██  ███    ██  ██  ███  █  █ ███  \n" \
               "█  █ █  █ █  █    █ █  █ █  █ █  █ █  █ \n" \
               "█  █ █  █ █  █    █ █    ███  ████ █  █ \n" \
               "███  ████ ███     █ █    █  █ █  █ ███  \n" \
               "█    █  █ █    █  █ █  █ █  █ █  █ █    \n" \
               "█    █  █ █     ██   ██  ███  █  █ █    "
    assert solution_2 == capitals
    print(f"Day ... part 2: {part_2} \n{solution_2}")

    print(f"Day ... took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
