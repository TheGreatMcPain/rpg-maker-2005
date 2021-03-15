#!/usr/bin/env python
# My attempt at turning the json data into the text file suitable
# for training GPT-2.
import json
import sys


def main():
    argv = sys.argv[1:]

    with open(argv[0], 'r') as f:
        storyData = json.load(f)

    storyTexts = storyDataToString(storyData)

    for x in storyTexts:
        print(x)

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
