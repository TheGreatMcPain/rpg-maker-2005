#!/usr/bin/env python
# My attempt at turning the json data into the text file suitable
# for training GPT-2.
import json
import sys
import argparse
import os


def main(argv):
    parser = argparse.ArgumentParser(
        description=
        "Convert JSON data from webscraper into a text dataset for GPT-2.")

    parser.add_argument('-i',
                        '--input',
                        dest='inputJSON',
                        metavar='<json file>',
                        type=str,
                        required=True,
                        help="Input JSON file")
    parser.add_argument('-o',
                        '--output',
                        dest='outputFile',
                        metavar='<output file>',
                        type=str,
                        required=True,
                        help="Output TEXT file")
    parser.add_argument('-n',
                        '--max-story-versions',
                        dest='maxStoryVersions',
                        metavar='<number>',
                        type=int,
                        required=False,
                        default=20,
                        help="Max number of versions of a story.")

    args = parser.parse_args(argv[1:])

    # Open json file and load it into storyData
    try:
        with open(args.inputJSON, 'r') as f:
            storyData = json.load(f)
    except IOError as e:
        print(e)
        exit(e.errno)
    except:
        print("Oops,", args.inputJSON, "failed to open.")
        exit(1)

    # Check if storyData is a list.
    # If not make it a list of one item.
    if not isinstance(storyData, list):
        storyData = [storyData]

    # Loop through each story in storyData, and
    # add them into one big list.
    storyTexts = []
    for story in storyData:
        storyTexts += storyDataToString(story)

    # Write the whole thing to file.
    try:
        with open(args.outputFile, "w") as outFile:
            for x in storyTexts:
                outFile.write(x)
    except IOError as e:
        print(e)
        exit(e.errno)
    except:
        print("Oops,", args.outputFile, "failed to write.")
        exit(1)

    print("Number of texts:", len(storyTexts))


def storyDataToString(storyData: dict,
                      storyTexts: list = [],
                      first: bool = True):
    # If there are only 2 keys then we can safely assume
    # that we've reached an ending.
    if len(storyData) == 2:
        storyTexts.append(makeStoryString(storyData))
        return

    for action in storyData['actions']:
        # Make a trail of bread crumbs by linking the current
        # 'storyData' to a new 'parent' attribute.
        action['parent'] = storyData

        storyDataToString(action, storyTexts, False)

    if first:
        return storyTexts


def makeStoryString(storyData: dict):
    # list of words that won't make since if we add "you"
    # in front of. (Pulled from AIDungeon github)
    dontAddYou = [
        "the",
        "another",
        "next",
        "in",
        "monday",
        "back",
        "a",
        "years",
        "one",
        "two",
        "during",
        "months",
        "weeks",
        "seven",
        "three",
        "...",
        "twelve",
        "four",
        "five",
        "six",
        "blackness...",
        "you",
        "no",
        "yes",
        "up",
        "down",
        "onward",
    ]

    storyText = "<|endoftext|>"

    while 'parent' in storyData.keys():
        storyData = storyData['parent']

        actionText = ""
        if 'action_text' in storyData.keys():
            firstWord = storyData['action_text'].split(" ")[0]
            if firstWord[-1] == ".":
                firstWord = firstWord[:-1]

            # Determine if firstWord is exists in dontAddYou
            if firstWord.lower() in dontAddYou:
                actionText = "> " + storyData['action_text'] + "\n"
            else:
                # Assume the action is dialogue if it's first
                # character is a double quote.
                if storyData['action_text'][0] == '"':
                    # Only add the quote.
                    lastQuote = storyData['action_text'].rfind('"')

                    actionText = "> You say " + storyData[
                        'action_text'][:lastQuote + 1] + "\n"
                else:
                    actionText = "> You " + storyData['action_text'][0].lower(
                    ) + storyData['action_text'][1:] + "\n"

        storyText = actionText + storyData['story_text'] + "\n" + storyText

    return storyText


if __name__ == "__main__":
    main(sys.argv)
