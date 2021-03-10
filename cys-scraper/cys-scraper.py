#!/usr/bin/env python
import json
import sys
import getopt
import os
from selenium import webdriver


# Copy the file 'config.json.sample' to 'config.json'
# and edit accordingly
def main():
    def printUsage():
        print("Usage:", sys.argv[0], "-s,--story-id <story id>",
              "-d,--depth <depth>", "-o,--output <output file>",
              "-h,--headless")

    # Get the absolute path of 'config.json'
    configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "config.json")

    # If 'config.json' exists attempt to load it
    # and configure the 'firefoxBinary' and 'geckodriver' variables
    if os.path.isfile(configPath):
        with open(configPath, 'r') as config:
            configJSON = json.load(config)

        firefoxBinary = configJSON['FIREFOX_BINARY']
        geckodriver = configJSON['GECKODRIVER']
    else:
        print("'config.json' was not found!")
        exit(1)

    # Ignore the script name
    argv = sys.argv[1:]

    storyID = None
    depth = None
    outputFile = None
    headless = False

    try:
        opts, args = getopt.getopt(
            argv, "s:d:o:h", ["story-id=", "depth=", "output=", "headless"])
    except:
        print("Error\n")
        printUsage()
        exit(1)

    if len(args) > 0:
        for arg in args:
            print(arg, "Is not valid")
        print()
        printUsage()
        exit(1)

    for opt, arg in opts:
        if opt in ['-s', '--story-id']:
            storyID = int(arg)
        elif opt in ['-d', '--depth']:
            depth = int(arg)
        elif opt in ['-o', '--output']:
            outputFile = arg
        elif opt in ['-h', '--headless']:
            headless = True

    if not storyID:
        print("storyID is missing")
        printUsage()
        exit(1)
    if not depth:
        print("Depth is missing")
        printUsage()
        exit(1)
    if not outputFile:
        print("Output is missing")
        printUsage()
        exit(1)

    browser = spawnBrowser(firefoxBinary, geckodriver, headless)

    storyData = getCYSStory(browser, storyID, depth)

    browser.close()

    actionCount, branches = getStoryStats(storyData)

    print("Total number of actions:", actionCount)
    print("Total branches that occur:", branches)

    # Dump results to a json file.
    with open(outputFile, 'w') as f:
        f.write(json.dumps(storyData, indent=2))


# returns a webdriver object
# firefoxBinary: path to firefox binary
# geckodriver:   path to geckodriver binary
# headless:      `True` means "don't show browser"
def spawnBrowser(firefoxBinary: str, geckodriver: str, headless: bool):
    options = webdriver.firefox.options.Options()
    options.headless = headless
    options.executable_path = geckodriver

    return webdriver.Firefox(executable_path=geckodriver,
                             options=options,
                             firefox_binary=firefoxBinary,
                             service_log_path=os.path.devnull)


# Returns a dictionary containing the contents of a ChooseYourStory story.
# browser: A webdriver object
# storyID: The last digits from a CYS story url
# depth:   How many choices deep to go. (negative numbers with disable this)
def getCYSStory(browser: webdriver, storyID: int, depth: int):
    storyLink = "https://chooseyourstory.com/story/viewer/default.aspx?StoryId="
    storyLink += str(storyID)

    # Don't open the link if we are already on it.
    if browser.current_url != storyLink:
        browser.get(storyLink)

    storyData = {}

    # TODO: Check if on a "Game Over" page.
    try:
        header = browser.find_element_by_xpath('/html/body/form/div[3]/h1')
    except:
        header = None

    if header:
        if "Rate" in header.text:
            return storyData

    if depth == 0:
        return storyData

    # Get the "story" text from the current page
    story_text = browser.find_element_by_xpath("/html/body/div[3]/div[1]").text

    storyData['story_text'] = story_text

    # Get All "choices" from current page
    links = browser.find_elements_by_xpath("/html/body/div[3]/ul/li")

    # Store the link's text in a list
    # (prevents 'ElementIsStale' errors)
    link_texts = [link.text for link in links]

    # Make recursive calls for each link found
    storyData['actions'] = []
    for link_text in link_texts:
        action = {}
        action['action_text'] = link_text

        # Search for the link based on its text and click on it.
        try:
            browser.find_element_by_link_text(link_text).click()
        except:
            continue

        # Get the contents of that action.
        action['action_contents'] = getCYSStory(browser, storyID, depth - 1)

        browser.back()

        # Add the results to our list of actions.
        storyData['actions'].append(action)

    return storyData


# Returns the number of actions, and branches in the story.
# storyData: A dictionary that contains the story data.
def getStoryStats(storyData: dict):
    actionCount = 0
    branches = 0

    if storyData == {}:
        return actionCount, branches

    actionCount += len(storyData['actions'])

    if actionCount > 1:
        branches += 1

    for action in storyData['actions']:
        returnValue = getStoryStats(action['action_contents'])
        actionCount += returnValue[0]
        branches += returnValue[1]

    return actionCount, branches


if __name__ == "__main__":
    main()
