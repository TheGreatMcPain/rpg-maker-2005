#!/usr/bin/env python
# My attempt at turning the json data into the text file suitable
# for training GPT-2.
import json
import sys
import argparse
import os
import random


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
    parser.add_argument('-s',
                        "--separate-at-num-actions",
                        dest='sepAtNumActions',
                        metavar='<number>',
                        type=int,
                        required=False,
                        default=0,
                        help="Insert <|endoftext|> at number of actions.")
    parser.add_argument('-e',
                        "--exclude-ids",
                        dest='excludeIds',
                        metavar='<list-of-ids>',
                        type=str,
                        required=False,
                        help="Comma separated list of ids to exclude.")

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

    # Remove anything from storyData that's in excludeIds
    if args.excludeIds:
        excludeIds = args.excludeIds.split(",")
        storyData = [x for x in storyData if x['story_id'] not in excludeIds]

    # Loop through each story in storyData, and
    # add them into one big list.
    storyLengths = []
    tempList = []
    storyTexts = []
    for story in storyData:
        storyLength = {}
        storyLength['title'] = story['story_title']
        tempList += storyDataToString(
            story, seperatorAtNumActions=args.sepAtNumActions)

        # Randomly shrink list if it's too big.
        if len(tempList) > args.maxStoryVersions:
            # Shuffle the list
            random.shuffle(tempList)

            # Shrink the list to the desired 'maxStoryVersions'
            del tempList[args.maxStoryVersions:]

        # Get length of data
        storyLength['length'] = 0
        for storyText in tempList:
            storyLength['length'] += len(storyText)

        storyLengths.append(storyLength)

        storyTexts += tempList
        tempList = []

    # Get the total length of the file as we write to it.
    totalLength = 0

    # Write the whole thing to file.
    try:
        with open(args.outputFile, "w") as outFile:
            for x in storyTexts:
                totalLength += len(x)
                outFile.write(x)
    except IOError as e:
        print(e)
        exit(e.errno)
    except:
        print("Oops,", args.outputFile, "failed to write.")
        exit(1)

    print("Number of texts:", len(storyTexts), end="\n\n")

    # Display the percentage of how much each story takes up in the file.
    for storyLength in storyLengths:
        percentage = (storyLength['length'] / totalLength) * 100

        print("Story title:", storyLength['title'])
        print("percentage in file:", percentage)
        print()


def storyDataToString(storyData: dict,
                      storyTexts: list = [],
                      first: bool = True,
                      seperatorAtNumActions: int = 0):
    # If there are only 2 keys then we can safely assume
    # that we've reached an ending.
    if len(storyData) == 2:
        storyTexts.append(makeStoryString(storyData, seperatorAtNumActions))
        return

    for action in storyData['actions']:
        # Make a trail of bread crumbs by linking the current
        # 'storyData' to a new 'parent' attribute.
        action['parent'] = storyData

        storyDataToString(action, storyTexts, False, seperatorAtNumActions)

    if first:
        return storyTexts


def makeStoryString(storyData: dict, seperatorAtNumActions: int = 0):
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
    counter = -1
    if seperatorAtNumActions > 0:
        counter = 0
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

        if (counter >= seperatorAtNumActions) and ('parent'
                                                   in storyData.keys()):
            storyText = actionText + "<|endoftext|>" + storyData[
                'story_text'] + "\n" + storyText
            counter = 0
        else:
            storyText = actionText + storyData['story_text'] + "\n" + storyText

            if (counter != -1):
                counter += 1

    return storyText


if __name__ == "__main__":
    main(sys.argv)
