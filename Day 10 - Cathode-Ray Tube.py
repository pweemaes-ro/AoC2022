"""Day 10: Cathode Ray Tube."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Callable, MutableSequence, Sequence
from typing import IO, Any, Final, TypeAlias, Optional

# type aliases for convenience and readability ;-)
Registers: TypeAlias = MutableSequence[int]
Params: TypeAlias = Sequence[Any]
Executor: TypeAlias = Callable[[Registers, Params], Registers]
ClockListenerCallback: TypeAlias = Callable[[int, Registers], None]


class CPUInstruction:
    """CPUInstruction class."""

    def __init__(self, name: str, cycles: int, executor: Executor) -> None:
        self.__name = name
        self.__cycles = cycles
        self.__executor = executor
        self.__params: Params = []

    def _params_setter(self, params: Params) -> None:
        """Property getter"""

        self.__params = params

    # noinspection PyArgumentEqualDefault
    # No need for a property getter, so must use functional way of creating
    # property? (Found no alternative on the web...)
    params = property(None, _params_setter, None,
                      "Set params for next execution")

    @property
    def name(self) -> str:
        """Return the name of the instruction."""

        return self.__name

    def execute(self, registers: Registers) -> Registers:
        """Execute this instruction (by calling its executor) using the
        params."""

        return self.__executor(registers, self.__params)

    @property
    def cycles(self) -> int:
        """Return the nr of cycles that execution of this instruction takes."""

        return self.__cycles


class ClockSignalListener(ABC):
    """Abstract base class for Clock Listeners."""

    def __init__(self, cpu: CPU) -> None:
        """Store the cpu and register yourself with the cpu."""

        self.__cpu = cpu
        cpu.register_listener(self)

    @abstractmethod
    def callback(self, cycle_nr: int, registers: Registers) -> None:
        """This must be implemented by concrete classes."""

        pass

    @abstractmethod
    def get_status(self) -> Any:
        """This must be implemented by concrete classes."""

        pass


class SignalStrengthListener(ClockSignalListener):
    """A concrete Clock Listener."""

    def __init__(self, cpu: CPU) -> None:
        super().__init__(cpu)
        self.__total_signal_strength = 0
        self.__next_cycle = 20

    def callback(self, cycle_nr: int, registers: Registers) -> None:
        """Update total signal strength if it's a cycle we're interested in.
        We are interested in cycles 20, 60, 100, 140 etc."""

        if cycle_nr == self.__next_cycle:
            self.__total_signal_strength += cycle_nr * registers[0]
            self.__next_cycle += 40

    def get_status(self) -> int:
        """Return the current value of the signal strength."""

        return self.__total_signal_strength


class CRT(ClockSignalListener):
    """The CRT listens to the clock, since every clock_tick it prints a pixel
    on the screen."""

    __lines: Final = 6
    __pix_per_line: Final = 40
    __display_chars = ('⚪', '🔴')

    def __init__(self, cpu: CPU) -> None:
        super().__init__(cpu)
        self.__screen = [[" "
                          for _ in range(self.__pix_per_line)]
                         for _ in range(self.__lines)]

    def callback(self, cycle_nr: int, registers: Registers) -> None:
        """Write a pixel. The location of the pixel to write is determined by
        the cycle_nr, the content of the pixel ("█" or " ") is determined by
        whether the crt horizontal position is one of the three horizontal
        positions taken up by the sprite (the middle of these is in
        register[0])."""

        crt_v_pos, crt_h_pos = divmod(cycle_nr - 1, self.__pix_per_line)

        if registers[0] - 1 <= crt_h_pos <= registers[0] + 1:
            display_char = self.__display_chars[1]
        else:
            display_char = self.__display_chars[0]

        self.__screen[crt_v_pos][crt_h_pos] = display_char

    def get_status(self) -> str:
        """Return the image on the CRT."""

        return '\n'.join(''.join(line) for line in self.__screen)


class CPU:
    """The CPU. Note that for simplicity, we've 'integrated' the clock and the
    CPU... The CPU makes the clock tick the required amount of times for each
    executed instruction (1 for noop, 2 for addx). Since the CPU controls the
    clock, the CPU is also where devices register if they want to be informed
    on every new cycle, and the CPU informs those devices (sharing the
    registers with these devices)."""

    __nr_registers: Final = 1       # Spec: The CPU has a single register.
    __registers_initial_value = 1   # Spec: Single register starts withvalue 1.

    def __init__(self,
                 supported_instructions: tuple[CPUInstruction, ...],
                 instruction_bus: IO[str]) -> None:
        """Initialize all class members."""

        self.__instructions = {instruction.name: instruction
                               for instruction in supported_instructions}
        self.__instruction_bus = instruction_bus
        self.__registers: Registers = [self.__registers_initial_value
                                       for _ in range(self.__nr_registers)]
        self.__cycle_count = 0
        self.__listeners: list[ClockSignalListener] = []

    def register_listener(self, listener: ClockSignalListener) -> None:
        """Register the listener."""

        self.__listeners.append(listener)

    def __increment_cycles(self, nr_to_add: int) -> None:
        """Update the cycle count (add one at the time, since all listeners
        expect to be called back on each new cycle)."""

        for i in range(nr_to_add):
            self.__cycle_count += 1
            for listener in self.__listeners:
                # Strictly speaking we should pass a COPY of the registers, so
                # no external device can accidentally modify them...
                listener.callback(self.__cycle_count, self.__registers)

    def __fetch_instruction(self) -> Optional[CPUInstruction]:
        """Return instruction (if any) from instruction bus. Return None when
        no more instructions available."""

        if not (line := self.__instruction_bus.readline()):
            return None

        parts = line.split()

        instruction_name, params = parts[0], parts[1:]
        instruction = self.__instructions[instruction_name]
        instruction.params = params

        return instruction

    def start(self) -> None:
        """Fetch and execute all instructions from the instructions bus."""

        while instruction := self.__fetch_instruction():
            self.__increment_cycles(instruction.cycles)
            self.__registers = instruction.execute(self.__registers)


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

    noop = CPUInstruction(name="noop",
                          cycles=1,
                          executor=noop_executor)

    addx = CPUInstruction(name="addx",
                          cycles=2,
                          executor=addx_executor)

    with open("input_files/day10.txt") as input_file:
        cpu = CPU(supported_instructions=(noop, addx),
                  instruction_bus=input_file)
        signal_strength_device = SignalStrengthListener(cpu)
        crt = CRT(cpu)
        cpu.start()

    solution_1 = signal_strength_device.get_status()
    solution_2 = crt.get_status()

    stop = time.perf_counter_ns()

    assert solution_1 == 14340
    print(f"Day 10 part 1: {part_1} {solution_1:_}")

    screen_image = \
        "🔴🔴🔴⚪⚪⚪🔴🔴⚪⚪🔴🔴🔴⚪⚪⚪⚪🔴🔴⚪⚪🔴🔴⚪⚪🔴🔴🔴⚪⚪🔴⚪⚪🔴⚪🔴🔴🔴⚪⚪\n" \
        "🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪⚪⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪\n" \
        "🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪⚪⚪⚪🔴⚪🔴⚪⚪⚪⚪🔴🔴🔴⚪⚪🔴🔴🔴🔴⚪🔴⚪⚪🔴⚪\n" \
        "🔴🔴🔴⚪⚪🔴🔴🔴🔴⚪🔴🔴🔴⚪⚪⚪⚪⚪🔴⚪🔴⚪⚪⚪⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴🔴🔴⚪⚪\n" \
        "🔴⚪⚪⚪⚪🔴⚪⚪🔴⚪🔴⚪⚪⚪⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪🔴⚪🔴⚪⚪⚪⚪\n" \
        "🔴⚪⚪⚪⚪🔴⚪⚪🔴⚪🔴⚪⚪⚪⚪⚪🔴🔴⚪⚪⚪🔴🔴⚪⚪🔴🔴🔴⚪⚪🔴⚪⚪🔴⚪🔴⚪⚪⚪⚪"
    # Fun fact: PyCharm COUNTS characters assuming all have standard width,
    # which means the above lines do NOT exceed 80 chars (the PEP8 limit),
    # since each line is only 41 chars...
    assert solution_2 == screen_image
    print(f"Day 10 part 2: {part_2} PAPJCBHP\n{solution_2}")

    print(f"Day 10 took {(stop - start) * 10 ** -6:.3f} ms")


if __name__ == "__main__":
    main()
