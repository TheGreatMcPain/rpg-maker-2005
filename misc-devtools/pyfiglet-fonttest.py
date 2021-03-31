#!/usr/bin/env python
"""
A script for testing out different fonts from the pyfiglet module.
"""
import pyfiglet
import os


def main():
    fontList = pyfiglet.FigletFont.getFonts()
    terminaCols = os.get_terminal_size()[0]
    selection = ""

    while True:
        if selection == "":
            print(getFontOptions(charLimit=terminaCols))

        selection = input("Enter number or 'exit': ")

        if selection == "":
            continue

        if selection.lower() == "exit":
            break

        try:
            font = fontList[int(selection)]
        except:
            print("Oof")

        print("Font name:", font)

        printStringAsFiglet("test", fontName=font)

    return 0


def printStringAsFiglet(inputStr: str, fontName: str):
    f = pyfiglet.Figlet(font=fontName)

    print(f.renderText(inputStr))


def getFontOptions(charLimit: int = 50):
    fontList = pyfiglet.FigletFont.getFonts()

    fontStringList = []
    for fontIndex in range(len(fontList)):
        fontStringList.append("{:03d}".format(fontIndex) + ": " +
                              fontList[fontIndex] + " ")

    fontNameMaxChars = max([len(x) for x in fontStringList])

    lineList = []
    line = ""
    for fontString in fontStringList:
        whiteSpace = fontNameMaxChars - len(fontString)
        line += fontString

        while whiteSpace > 0:
            line += " "
            whiteSpace -= 1

        if len(line) > charLimit - 30:
            lineList.append(line)
            line = ""

    outputString = ""
    for line in lineList:
        outputString += line + "\n"

    return outputString


if __name__ == "__main__":
    main()
