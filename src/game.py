#!/usr/bin/env python
from .model_manager import ModelManager
from .story_manager import StoryManager
from .story_starter import StoryStarter
import datetime
import os
import re


class Game:
    def __init__(self, modelManager: ModelManager, transcriptPath: str,
                 savesPath: str, storiesJSON: str):
        self.keepGoing = True
        self.firstAction = True
        self.modelManager = modelManager
        self.storyManager = None
        self.transcriptPath = transcriptPath
        self.savesPath = savesPath
        self.storiesJSON = storiesJSON
        self.storyStarter = StoryStarter(self.storiesJSON)

        self.oldText = ""  # Used for the help function
        self._remember = False

        self.currentText = ""
        self.currentAction = ""

        # Will use the current date to make a save file.
        self.curSaveFile = datetime.datetime.now().strftime(
            "%Y-%m-%d_%Hh_%Mm_%Ss")

        # Create StoryManager Object
        self.storyManager = StoryManager(self.curSaveFile + ".json",
                                         self.savesPath,
                                         memorySize=15)

        return

    def help(self):
        helpText = "After each prompt type a command, for example: \n"
        helpText += "> go to the town\n\n"
        helpText += "For dialouge use double quotes (\"), for example: \n"
        helpText += "> \"hello\" \n\n"
        helpText += "To type a command, type \"/\" in front of the command\n"
        helpText += "Available Commands:\n"
        helpText += "help - Displays a list of commands\n"
        helpText += "quit - quits the adventure\n"
        helpText += "transcript - saves the adventure to a file\n"
        helpText += "remember - marks the last action as important\n"
        helpText += "rewind - rewind the previous action\n"
        helpText += "retry - send the last action back into the bot\n"

        return helpText

    def quitGame(self):
        self.keepGoing = False

    def transcript(self, fileName: str):
        if fileName.split('.')[-1].lower() != ".txt":
            fileName += ".txt"

        filePath = os.path.join(self.transcriptPath, fileName)

        with open(filePath, 'w') as transcriptFile:
            transcriptFile.write(self.storyManager.getTranscript() + "\n" +
                                 self.currentText)

    # Reverts to the previous incase the user wants to change it
    # for a better AI response.
    def rewind(self):
        # revert the previous action
        aiText = self.storyManager.revertAction()

        self.currentText = aiText

    # Simply reruns the AI with the current text.
    def retry(self):
        aiText = self.modelManager.getSampleFromText(
            self.storyManager.getAISeed())
        self.currentAction = self._stripAIText(aiText)

    # All this does is initialize the 'self.currentText'
    def startGame(self,
                  genre: str,
                  characterName: str,
                  characterClass: str,
                  customPrompt: str = None):
        # Get the initial prompt from the StoryStarter
        if genre == "custom" and customPrompt != None:
            initialPrompt = customPrompt
        else:
            initialPrompt = self.storyStarter.getPrompt(
                genre, characterName, characterClass)

        # Lets add our game info into the storyData
        self.storyManager.storyData['genre'] = genre
        self.storyManager.storyData['class'] = characterClass
        self.storyManager.storyData['player'] = characterName

        self.currentText = initialPrompt

    # Simply resume the loaded game. (Also returns transcript)
    def resumeGame(self):
        self.currentText = self.storyManager.storyData['currentPrompt']
        self.firstAction = False
        return self.storyManager.getTranscript()

    def prepareAction(self, actionText):
        # Stuff for translating first person to second person
        # Pulled from...
        # https://github.com/Latitude-Archives/AIDungeon/blob/develop/story/utils.py

        # Capitalizing the first word in every sentence.
        def capitalizeFirstLetters(text):
            def capitalizeHelper(string):
                stringList = list(string)
                stringList[0] = stringList[0].upper()
                return "".join(stringList)

            firstLettersRegex = re.compile(r"((?<=[\.\?!]\s)(\w+)|(^\w+))")

            def cap(match):
                return capitalizeHelper(match.group())

            result = firstLettersRegex.sub(cap, text)
            return result

        # Simply capitalize the first letter in a word.
        def capitalize(word):
            return word[0].upper() + word[1:]

        # Generates variations of firstToSecondMappings
        def mappingVariationPairs(mapping: tuple):
            mappingList = []
            mappingList.append(
                (" " + mapping[0] + " ", " " + mapping[1] + " "))
            mappingList.append((" " + capitalize(mapping[0]) + " ",
                                " " + capitalize(mapping[1]) + " "))

            # Change you before punctuation
            if mapping[0] == "you":
                mapping = ("you", "me")
            mappingList.append(
                (" " + mapping[0] + ",", " " + mapping[1] + ","))
            mappingList.append(
                (" " + mapping[0] + "\?", " " + mapping[1] + "\?"))
            mappingList.append(
                (" " + mapping[0] + "\!", " " + mapping[1] + "\!"))
            mappingList.append(
                (" " + mapping[0] + "\.", " " + mapping[1] + "."))

            return mappingList

        # Replace text, but only outside of quotations
        def replaceOutsideQuotes(text, currentWord, replWord):
            regExpr = re.compile(currentWord + '(?=([^"]*"[^"]*")*[^"]*$)')

            output = regExpr.sub(replWord, text)
            return output

        firstToSecondMappings = [
            ("I'm", "you're"),
            ("Im", "you're"),
            ("Ive", "you've"),
            ("I am", "you are"),
            ("was I", "were you"),
            ("am I", "are you"),
            ("wasn't I", "weren't you"),
            ("I", "you"),
            ("I'd", "you'd"),
            ("i", "you"),
            ("I've", "you've"),
            ("was I", "were you"),
            ("am I", "are you"),
            ("wasn't I", "weren't you"),
            ("I", "you"),
            ("I'd", "you'd"),
            ("i", "you"),
            ("I've", "you've"),
            ("I was", "you were"),
            ("my", "your"),
            ("we", "you"),
            ("we're", "you're"),
            ("mine", "yours"),
            ("me", "you"),
            ("us", "you"),
            ("our", "your"),
            ("I'll", "you'll"),
            ("myself", "yourself"),
        ]

        # Lets first remove any whitespace
        actionText = actionText.strip()

        # Check if the input is dialogue
        if actionText[0] == '"':
            actionText = "You say, " + actionText
        else:
            # If not add 'You' if needed.
            if "you" not in actionText[:6].lower(
            ) and "I" not in actionText[:6]:
                actionText = actionText[0].lower() + actionText[1:]
                actionText = "You " + actionText

            # Make sure we add punctuation
            if actionText[-1] not in [".", "?", "!"]:
                actionText = actionText + "."

        # Translate first person text into second person text.
        actionText = " " + actionText
        for pair in firstToSecondMappings:
            variations = mappingVariationPairs(pair)
            for variation in variations:
                actionText = replaceOutsideQuotes(actionText, variation[0],
                                                  variation[1])

        actionText = actionText.strip()
        actionText = capitalizeFirstLetters(actionText)

        return actionText

    def _stripAIText(self, inputText):
        # First lets fix any weird punctuation.
        inputText = inputText.replace("’", "'")
        inputText = inputText.replace("`", "'")
        inputText = inputText.replace("“", '"')
        inputText = inputText.replace("”", '"')

        # Find the last sentence
        lastIndex = max(inputText.rfind("."), inputText.rfind("?"),
                        inputText.rfind("!"))

        # If we can't just use what ever is there
        if lastIndex <= 0:
            lastIndex = len(inputText) - 1

        # Check for "<|endoftext|>"
        etToken = inputText.find("<")
        if etToken > 0:
            lastIndex = min(lastIndex, etToken - 1)

        # Check for actions.
        actToken = inputText.find(">")
        if actToken > 0:
            lastIndex = min(lastIndex, actToken - 1)

        inputText = inputText[:lastIndex + 1]

        # Remove trailing quotes
        numQuotes = inputText.count('"')
        if not numQuotes % 2 == 0:
            finalInd = inputText.rfind('"')
            inputText = inputText[:finalInd]

        # Remove trailing actions that don't have ">" in front.
        lines = inputText.split("\n")
        lastLine = lines[-1]
        if ("you ask" in lastLine or "You ask" in lastLine or "you say"
                in lastLine or "You say" in lastLine) and len(lines) > 1:
            inputText = "\n".join(lines[0:-1])

        return inputText

    def gameCommand(self, inputStr: str):
        # If help was ran previously reset self.oldText
        if self.oldText != "":
            self.currentText = self.oldText
            self.oldText = ""

        # If the input is empty lets, just treat like the user
        # wants to continue.
        if inputStr == "":
            inputStr = "continue"

        # If this is the first run lets set remember.
        if self.firstAction:
            self._remember = True

        # remove whitespace from left of string.
        inputStr = inputStr.lstrip()
        # Check if command
        if inputStr[0] == '/':
            inputStr = inputStr[1:].strip()
            if inputStr == "quit":
                # do exit
                self.quitGame()
                return
            elif inputStr == "remember":
                # Will mark next action as important
                self._remember = True
                return
            elif "transcript" in inputStr:
                # Get the argument from inputStr
                arg = inputStr.replace("transcript", "").lstrip()
                self.transcript(arg)
                return
            elif inputStr == "rewind":
                # do rewind
                self.rewind()
                return
            elif inputStr == "retry":
                # do retry
                self.retry()
                return
            elif inputStr == "help":
                # do help
                self.oldText = self.currentText
                self.currentText = self.help()
                return
            else:
                # do nothing if invalid.
                self.currentText = "Invalid command. See '/help'"
                return

        # Do main loop
        userText = self.prepareAction(inputStr)
        curAction = self.storyManager.createAction(self.currentText, userText)

        # Takes the current action and saves it for seed generation
        # to send to the AI
        if self._remember:
            self.storyManager.saveAction(curAction)
            self._remember = False
        self.storyManager.updateMemory(curAction)
        aiSeed = self.storyManager.getAISeed()

        self.firstAction = False

        # Send the seed to the AI
        aiOutput = self.modelManager.getSampleFromText(aiSeed)
        self.currentText = self._stripAIText(aiOutput)
        self.storyManager.updateCurrentPrompt(self.currentText)
