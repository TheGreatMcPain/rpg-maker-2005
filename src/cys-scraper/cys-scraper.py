#!/usr/bin/env python
import json
import sys
import os
import reprint
import time
import argparse
import random
from selenium import webdriver

# Global script start time.
START_TIME = time.time()


# Copy the file 'config.json.sample' to 'config.json'
# and edit accordingly
def main(argv):
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

    # Setup program arguments.
    parser = argparse.ArgumentParser(
        description="WebScraper for ChooseYourStory")
    parser.add_argument(
        '-s',
        '--story-id',
        dest='storyID',
        metavar='<storyid, storyids>',
        type=str,
        required=True,
        help=
        "The ChooseYourStory storyid or a comma separated list of storyids.")
    parser.add_argument('-d',
                        '--depth',
                        dest='depth',
                        metavar='<depth size>',
                        type=int,
                        required=False,
                        default=-1,
                        help="How many choices deep we should scrape.")
    parser.add_argument('-o',
                        '--output-json',
                        dest='outputFile',
                        metavar="<output json>",
                        type=str,
                        required=True,
                        help="Output JSON file.")
    parser.add_argument('-u',
                        '--update-json',
                        dest='updateJson',
                        action='store_true',
                        help="Update json file (Don't overwrite old ids)")
    parser.add_argument('-n',
                        '--headless',
                        dest='headless',
                        action='store_true',
                        help="Hides the browser window")
    parser.add_argument(
        '-r',
        '--random',
        dest='randomNum',
        metavar="<number of paths>",
        type=int,
        required=False,
        help="Pick random story paths instead of searching for all of them.")

    parser.set_defaults(updateJson=False)
    parser.set_defaults(headless=False)

    # Parse arguments
    args = parser.parse_args(argv)

    # Setup variables
    storyIDs = [int(x) for x in args.storyID.split(",")]
    depth = args.depth
    outputFile = args.outputFile
    headless = args.headless
    storyDataList = []

    # Load json file if update is set.
    if args.updateJson:
        if os.path.isfile(outputFile):
            with open(outputFile, 'r') as f:
                storyDataList = json.load(f)

    # Remove any storyIDs that are already in the json file.
    if len(storyDataList) > 0:
        currentIds = [int(x['story_id']) for x in storyDataList]
        storyIDs = [x for x in storyIDs if x not in currentIds]
    print(storyIDs)

    browser = spawnBrowser(firefoxBinary, geckodriver, headless)

    # Use reprint.output to print status to the terminal.
    #
    # (Basically anytime the list 'status_list' changes within
    #  the 'with' block the terminal output will change too.)
    with reprint.output(output_type="list", interval=0) as status_list:
        for storyID in storyIDs:
            # Initial message
            status_list.clear()
            status_list.append("Scraping StoryID: " + str(storyID))
            status_list.append("Elapsed Time (secs): " +
                               str(int(time.time() - START_TIME)))
            status_list.append("Current Action: (Nothing to show yet)")
            status_list.append(
                "Number of other actions: (Nothing to show yet)")

            if args.randomNum:
                storyData = {}
                for _ in range(args.randomNum):
                    getCYSStoryRand(browser, storyID, storyData, status_list)
            else:
                storyData = getCYSStory(browser, storyID, depth, {},
                                        status_list)
            storyDataList.append(storyData)

        # Clear output (Prevents any terminal output weirdness)
        status_list.clear()

    browser.close()

    print("Finished!\n")
    print("Total Runtime (secs):", int(time.time() - START_TIME), end="\n\n")
    for storyData in storyDataList:
        actionCount, branches, endings = getStoryStats(storyData)
        print("Story title:", storyData['story_title'])
        print("Story ID:", storyData['story_id'])
        print("Total number of actions:", actionCount)
        print("Total branches that occur:", branches)
        print("Total number of possible endings:", endings)
        print()

    # Dump results to a json file.
    with open(outputFile, 'w') as f:
        if len(storyDataList) > 1:
            f.write(json.dumps(storyDataList, indent=2))
        else:
            f.write(json.dumps(storyDataList[0], indent=2))


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
# browser:     A webdriver object
# storyID:     The last digits from a CYS story url
# depth:       How many choices deep to go. (negative numbers with disable this)
# frontier:    A dictionary for keeping track of already visited pages and actions.
# status_list: The list from 'reprint.output()'
def getCYSStory(browser: webdriver, storyID: int, depth: int, frontier: dict,
                status_list: list):
    # Updates the second, third, and fourth lines of the terminal output.
    def updateStatus(currentAction: dict, status_list: list):

        # Don't even try to access an empty dictionary.
        if len(currentAction) != 1:
            status_list[1] = "Elapsed Time (secs): " + str(
                int(time.time() - START_TIME))

            status_list[2] = "Current Action: " + currentAction['action_text']

            status_list[3] = "Number of other actions: " + str(
                len(currentAction['actions']))

    storyLink = "https://chooseyourstory.com/story/viewer/default.aspx?StoryId="
    storyLink += str(storyID)

    storyData = {}

    # Don't open the link if we are already on it.
    if browser.current_url != storyLink:
        browser.get(storyLink)

        # Since this is the first instance of the function lets
        # also store the story's title and id for later use.
        storyData['story_title'] = browser.title.split(" :: ")[0]
        storyData['story_id'] = str(storyID)

    # Check if on a "Rate this story" page.
    try:
        header = browser.find_element_by_xpath('/html/body/form/div[3]/h1')
    except:
        header = None

    # Stop if we are on a "Rate this story" page.
    if header:
        if "Rate" in header.text:
            return storyData

    if depth == 0:
        return storyData

    # Get the "story" text from the current page
    story_text = browser.find_element_by_xpath("/html/body/div[3]/div[1]").text
    page_title = browser.find_element_by_xpath("/html/body/div[2]/h1").text

    storyData['story_text'] = story_text

    page_contents = page_title + "\n" + story_text

    # Store the story_text in the 'frontier'
    if page_contents not in frontier.keys():
        frontier[page_contents] = []

    # Get All "choices" from current page
    links = browser.find_elements_by_xpath("/html/body/div[3]/ul/li")

    # Store the link's text in a list
    # (prevents 'ElementIsStale' errors)
    link_texts = [link.text for link in links]

    # Filter the `list_texts` using the frontier.
    link_texts = list(set(link_texts) - set(frontier[page_contents]))
    link_texts.sort()

    # Make recursive calls for each link found
    storyData['actions'] = []
    for link_text in link_texts:
        action = {}
        action['action_text'] = link_text

        # Search for the link based on its text and click on it.
        try:
            browser.find_element_by_link_text(link_text).click()

            # If it worked we can add the 'action' to the frontier.
            frontier[page_contents].append(link_text)
        except:
            continue

        # Get the contents of that action.
        action.update(
            getCYSStory(browser, storyID, depth - 1, frontier, status_list))

        browser.back()

        # Add the results to our list of actions.
        storyData['actions'].append(action)

        # Update terminal output.
        updateStatus(action, status_list)

    # Remove this story_title from the frontier.
    if page_contents in frontier.keys():
        frontier.pop(page_contents)

    return storyData


# Instead of attempting to scrape the whole story lets just have the scraper
# attempt to grab one story from a random path of actions.
# browser: webdriver from selenium
# storyID: The ChooseYourStory url number.
# storyData: An input dictionary.
# status_list: print list from reprint.
def getCYSStoryRand(browser: webdriver, storyID: int, storyData: dict,
                    status_list: list):
    # Updates the second, third, and fourth lines of the terminal output.
    def updateStatus(currentAction: dict, status_list: list):

        # Don't even try to access an empty dictionary.
        if len(currentAction) != 1:
            status_list[1] = "Elapsed Time (secs): " + str(
                int(time.time() - START_TIME))

            status_list[2] = "Current Action: " + currentAction['action_text']
            status_list[3] = "Number of other actions: <N/A>"

    storyLink = "https://chooseyourstory.com/story/viewer/default.aspx?StoryId="
    storyLink += str(storyID)

    # Don't open the link if we are already on it.
    if browser.current_url != storyLink:
        browser.get(storyLink)

        # Since this is the first instance of the function lets
        # also store the story's title and id for later use.
        if ('story_id' not in storyData.keys()):
            storyData['story_title'] = browser.title.split(" :: ")[0]
            storyData['story_id'] = str(storyID)

    # Check if on a "Rate this story" page.
    try:
        header = browser.find_element_by_xpath('/html/body/form/div[3]/h1')
    except:
        header = None

    # Stop if we are on a "Rate this story" page.
    if header:
        if "Rate" in header.text:
            return

    # Get the "story" text from the current page
    story_text = browser.find_element_by_xpath("/html/body/div[3]/div[1]").text

    # Don't create duplicate
    if 'story_text' not in storyData.keys():
        storyData['story_text'] = story_text

    # Get All "choices" from current page
    links = browser.find_elements_by_xpath("/html/body/div[3]/ul/li")

    # Store the link's text in a list
    # (prevent 'ElementIsStale' errors)
    link_texts = [link.text for link in links]
    pick_link = random.choice(link_texts)

    # Attempt to find the link in an exiting actions list
    existingAction = None
    if 'actions' in storyData.keys():
        for action in storyData['actions']:
            if action['action_text'] == pick_link:
                existingAction = action
                break

    # Don't empty the actions list if one exists
    if 'actions' not in storyData.keys():
        storyData['actions'] = []

    # Keep picking links until we manage to get one.
    # If we found an existiing action this shouldn't need to pick again.
    while True:
        try:
            browser.find_element_by_link_text(pick_link).click()
            break
        except:
            pick_link = random.choice(link_texts)

    # If we did find an exising action use it.
    action = {}
    if existingAction:
        action = existingAction
    else:
        action['action_text'] = pick_link

    updateStatus(action, status_list)

    # Since we are passing the action as the recursive call's 'storyData'
    # I would assume that 'action' will get updated.
    getCYSStoryRand(browser, storyID, action, status_list)

    browser.back()

    if not existingAction:
        storyData['actions'].append(action)

    return


# Returns the number of actions, and branches in the story.
# storyData: A dictionary that contains the story data.
def getStoryStats(storyData: dict):
    actionCount = 0
    branches = 0
    endings = 0

    if len(storyData) == 1:
        endings += 1
        return actionCount, branches, endings

    actionCount += len(storyData['actions'])

    if actionCount > 1:
        branches += 1

    for action in storyData['actions']:
        returnValue = getStoryStats(action)
        actionCount += returnValue[0]
        branches += returnValue[1]
        endings += returnValue[2]

    return actionCount, branches, endings


if __name__ == "__main__":
    main(sys.argv[1:])
