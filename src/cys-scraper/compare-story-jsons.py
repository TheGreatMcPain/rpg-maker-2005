#!/usr/bin/env python
# Compares two storyData files and print "same" if they are equal,
# or "not the same" if they are different.
import json
import os
import sys


def main():
    def printUsage():
        print("Compares two story json files",
              "(For testing changes to webscraper)")
        print(
            "Prints 'same' if they are the same, or 'not the same' if not.\n")
        print("Usage:", os.path.basename(sys.argv[0]),
              "<story1.json> <story2.json>\n")

    args = sys.argv[1:]

    if len(args) < 2:
        printUsage()
        exit(1)

    if not os.path.isfile(args[0]) and os.path.isfile(args[1]):
        print("One of input files don't exist.")
        exit(1)

    json1 = loadJSON(args[0])
    json2 = loadJSON(args[1])

    if compareStories(json1, json2):
        print("same")
    else:
        print("not the same")


def loadJSON(jsonfile: str):
    data = None

    with open(jsonfile, 'r') as f:
        data = json.load(f)

    if data:
        return data
    else:
        print("Something broke. :(")
        exit(1)


def compareStories(storyData1, storyData2):
    result = True
    if 'story_title' in storyData1.keys():
        if storyData1['story_title'] != storyData2['story_title']:
            return False

    if 'story_id' in storyData1.keys():
        if storyData1['story_id'] != storyData2['story_id']:
            return False

    if (len(storyData1) == 1) and (len(storyData2) == 1):
        return result

    if storyData1['story_text'] != storyData2['story_text']:
        return False

    if len(storyData1['actions']) != len(storyData2['actions']):
        return False

    for index in range(0, len(storyData1['actions'])):
        action1 = storyData1['actions'][index]
        action2 = None

        # Since we can't sort the action lists will need to simply
        # search for the same action_text.
        for action2loop in storyData2['actions']:
            if action1['action_text'] == action2loop['action_text']:
                action2 = action2loop
                break

        # Assume the actions are not the same if action2 is still None.
        if not action2:
            return False

        result = compareStories(action1, action2)

    return result


if __name__ == "__main__":
    main()
