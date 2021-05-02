#!/usr/bin/env python
import time
import random
import pyfiglet
import os


def main():
    showIntro()


def showIntro():
    terminalWidth = os.get_terminal_size()[0]
    gameNameFont = "larry3d"
    if terminalWidth < 84:
        gameNameFont = "doom"

    maker = "RPGMaker2005"
    presents = "Proudly Presents"
    dots = "..."
    gameName = ("NotAnother", "AIDungeon")

    slowPrint(getFigletString(maker, "small"), 500, 1000, True)

    slowPrint(presents, 5, 10, False)
    slowPrint(dots, 2, 2, True)
    print()

    for x in gameName:
        slowPrint(getFigletString(x, font=gameNameFont), 500, 700, False)


def getFigletString(inputStr: str, font: str = "standard"):
    f = pyfiglet.Figlet(font=font)
    f.width = os.get_terminal_size()[0]

    return f.renderText(inputStr)


# Print a string in a way that looks like typing.
# input_str: The input string
# range1:    The first value passed to random.randint()
# range2:    The second value passed to random.randint()
# newline:   End the print with a print()
def slowPrint(inputStr: str, range1: int, range2: int, newline: bool):
    for x in inputStr:
        print(x, end="", flush=True)
        time.sleep(1 / random.randint(range1, range2))

    if newline:
        print()


if __name__ == "__main__":
    main()
