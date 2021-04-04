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
                 memorySize: int = 15):
        self.storyDirectory = os.path.abspath(storyDirectory)
        self.storyFile = os.path.join(self.storyDirectory, storyFile)
        self.storyData = {}
        self.memorySize = memorySize

        # If file exists load it into self.storyData
        if os.path.isfile(self.storyFile):
            self.storyData = json.loads(self.storyFile)
        else:
            # if it doesn't exist initialize dictionary
            self.storyData['transcript'] = []
            self.storyData['curMemory'] = []
            self.storyData['savedActions'] = []

    # Add starting action.
    def initializeStory(self, startText: str, userText: str):
        action = self.createAction(startText, userText)

        self.updateMemory(action)

        self.saveAction(action)

        # Save storyData to file
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
        # TODO
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

    # Generates a string for the AI model using the contents of
    # storyData['savedActions'] and storyData['curMemory']
    def getAISeed(self):
        seed = ""
        # TODO
        return seed

    # Generates a string containing the entire storyData['transcript']
    def getTranscript(self):
        transcript = ""
        # TODO
        return transcript
