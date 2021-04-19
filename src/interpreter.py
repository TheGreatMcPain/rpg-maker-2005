#!/usr/bin/env python


def gameCommand(inputStr: str):
    # remove whitespace from left of string.
    inputStr = inputStr.lstrip()
    # Check if command
    if inputStr[0] == '/':
        inputStr = inputStr[1:].strip()
        if inputStr == "quit":
            # do exit
            return
        elif inputStr == "remember":
            # do remember
            return
        elif inputStr == "transcript":
            # do transcript
            return
        elif inputStr == "retry":
            # do retry
            return
        elif inputStr == "help":
            # do help
            return

    # Do main loop
