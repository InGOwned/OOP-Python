from enum import Enum
from typing import Tuple


class ANSI:
    RESET = "\033[0m"
    MOVE = "\033[{row};{col}H"


class Color(Enum):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


RUS_ALPHABET = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"


def load_font(path: str, alphabet: str) -> dict[str, list[str]]:
    with open(path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]

    total_lines = len(lines)
    letters_count = len(alphabet)

    if total_lines % letters_count != 0:
        raise ValueError(
            "Невозможно определить высоту шрифта: "
            "число строк не кратно числу букв"
        )

    height = total_lines // letters_count

    blocks = [
        lines[i:i + height]
        for i in range(0, total_lines, height)
    ]

    return dict(zip(alphabet, blocks))


class Printer:
    _font = load_font("fonts/font7.txt", RUS_ALPHABET)

    def __init__(self, color, position, symbol="*"):
        self.color = color
        self.row, self.col = position
        self.symbol = symbol

    def __enter__(self):
        print(self.color.value, end="")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(ANSI.RESET, end="")

    @classmethod
    def print(cls, text, color, position, symbol="*"):
        with cls(color, position, symbol) as p:
            p._print_text(text)

    def _print_text(self, text: str):
        height = len(next(iter(self._font.values())))
        y = self.row
        x = self.col

        for ch in text:
            if ch == " ":
                x += 4
                continue

            if ch not in self._font:
                continue

            pattern = self._font[ch]
            width = max(len(line) for line in pattern)

            for i, line in enumerate(pattern):
                print(
                    ANSI.MOVE.format(row=y + i, col=x) +
                    line.replace("*", self.symbol)
                )

            x += width + 2


# Демонстрация работы

Printer.print(
    "ПРИВЕТ",
    Color.CYAN,
    (7, 5),
    "#"
)

with Printer(Color.GREEN, (17, 5), "@") as p:
    p._print_text("ШРИФТ")
