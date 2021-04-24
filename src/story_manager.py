#!/usr/bin/env python
# This class will be used to manage the user's current story,
# but can also be used to generate text for the AI model to process.
#
# The dictionary format is as follows...
#
# storyData = {}
#
# // The complete game transcript from start to finish.
# storyData['transcript'] = []
#
# // The last set of actions that will be sent to the AI.
# storyData['curMemory'] = []
#
# // Any points in the story that the user has saved.
# storyData['savedActions'] = []
#
# Each item in each list will contain an action.
#
# This 'action' dictionary will look like this...
#
# action = {}
# action['aiText'] = "<insert ai generate text>"
# action['userText'] = "<insert user's text>"
import json
import os


class StoryManager:
    def __init__(self,
                 storyFile: str,
                 storyDirectory: str,
                 memorySize: int = 5):
        self.storyDirectory = os.path.abspath(storyDirectory)
        self.storyFile = os.path.join(self.storyDirectory, storyFile)
        self.storyData = {}
        self.memorySize = memorySize

        # If file exists load it into self.storyData
        if os.path.isfile(self.storyFile):
            with open(self.storyFile, "r") as f:
                self.storyData = json.load(f)
        else:
            # if it doesn't exist initialize dictionary
            self.storyData['genre'] = ""
            self.storyData['class'] = ""
            self.storyData['player'] = ""
            self.storyData['currentPrompt'] = ""
            self.storyData['transcript'] = []
            self.storyData['curMemory'] = []
            self.storyData['savedActions'] = []

    # Load saveData from file.
    def loadStoryData(self, filePath):
        if not os.path.isfile(filePath):
            return False

        with open(filePath, "r") as f:
            self.storyData = json.load(f)
        self.storyFile = filePath

        return True

    # Change save location. (Also, removes the old file)
    def changeStoryFile(self, storyFile: str):
        # Store the old storyFile location
        oldStoryFile = self.storyFile
        # Update the storyFile location
        self.storyFile = os.path.join(self.storyDirectory, storyFile)
        # Dump the current save data into the new file.
        self.saveStory()
        # Delete the old file.
        os.remove(oldStoryFile)

    def updateCurrentPrompt(self, newPrompt: str):
        self.storyData['currentPrompt'] = newPrompt
        self.saveStory()

    # Updates self.storyData['curMemory'] and self.storyData['transcript']
    def updateMemory(self, action: dict):
        self.storyData['transcript'].append(action)

        self.storyData['curMemory'].append(action)

        # Reduce self.storyData['curMemory'] to memorySize
        if len(self.storyData['curMemory']) > self.memorySize:
            index = len(self.storyData['curMemory']) - self.memorySize
            self.storyData['curMemory'] = self.storyData['curMemory'][index:]

        # Save storyData to file
        self.saveStory()

    # Updates self.storyData['savedActions']
    def saveAction(self, action: dict):
        self.storyData['savedActions'].append(action)

        self.saveStory()

    # Save storyData to json
    def saveStory(self):
        with open(self.storyFile, "w") as f:
            f.write(json.dumps(self.storyData, indent=2))

    # Create action dictionary
    def createAction(self, aiText: str, userText: str):
        action = {}
        action['aiText'] = aiText
        action['userText'] = userText

        return action

    # Revert previous action (returns last aiText)
    def revertAction(self):
        lastAction = self.storyData['curMemory'].pop()
        # Also remove from transcript
        self.storyData['transcript'].pop()

        # If lastAction exists in savedActions remove it from there.
        if lastAction in self.storyData['savedActions']:
            self.storyData['savedActions'].remove(lastAction)

        # Return the aiText from that action
        return lastAction['aiText']

    # Generates a string for the AI model using the contents of
    # storyData['savedActions'] and storyData['curMemory']
    def getAISeed(self):
        seed = ""

        for action in self.storyData['savedActions']:
            if action not in self.storyData['curMemory']:
                seed += action['aiText'] + '\n> ' + action['userText'] + '\n'

        for action in self.storyData['curMemory']:
            seed += action['aiText'] + '\n> ' + action['userText'] + '\n'

        return seed

    # Generates a string containing the entire storyData['transcript']
    def getTranscript(self):
        transcript = ""

        for action in self.storyData['transcript']:
            transcript += action['aiText'] + '\n> ' + action['userText'] + '\n'

        return transcript
