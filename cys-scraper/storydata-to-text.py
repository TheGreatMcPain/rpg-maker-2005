#!/usr/bin/env python
# My attempt at turning the json data into the text file suitable
# for training GPT-2.
import json
import sys
import os


def main():
    def printUsage():
        print("Usage:", os.path.basename(sys.argv[0]),
              "<input.json> <output.txt>")

    if len(sys.argv) == 1:
        print("Convert story data from json to text for GPT-2 training.\n")
        printUsage()
        exit()

    argv = sys.argv[1:]

    if len(argv) < 2:
        printUsage()
        exit(1)

    # Open json file and load it into storyData
    try:
        with open(argv[0], 'r') as f:
            storyData = json.load(f)
    except IOError as e:
        print(e)
        exit(e.errno)
    except:
        print("Oops,", argv[0], "failed to open.")
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
        with open(argv[1], "w") as outFile:
            for x in storyTexts:
                outFile.write(x)
    except IOError as e:
        print(e)
        exit(e.errno)
    except:
        print("Oops,", argv[1], "failed to write.")
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
    storyText = "<|endoftext|>"

    while 'parent' in storyData.keys():
        storyData = storyData['parent']

        actionText = ""
        if 'action_text' in storyData.keys():
            actionText = "> " + storyData['action_text'] + "\n"

        storyText = actionText + storyData['story_text'] + "\n" + storyText

    return storyText


if __name__ == "__main__":
    main()
