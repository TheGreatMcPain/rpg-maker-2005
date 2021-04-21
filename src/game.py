#!/usr/bin/env python
from .model_manager import ModelManager
from .story_manager import StoryManager
from .storyStarter import StoryStarter
import datetime
import os


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
            transcriptFile.write(self.storyManager.getTranscript())

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
    def startGame(self, genre: str, characterName: str, characterClass: str):
        # Get the initial prompt from the StoryStarter
        initialPrompt = self.storyStarter.getPrompt(genre, characterName,
                                                    characterClass)
        # Lets let the AI generate the initial prompt.
        self.currentText = self._stripAIText(
            self.modelManager.getSampleFromText(initialPrompt))

    def _prepareAction(self, action_text):
        first_word = action_text.split(" ")[0]

        if first_word[0] == '"':
            action_text = "You say, " + action_text
        else:
            action_text = action_text[0].lower() + action_text[1:]
            action_text = "You " + action_text

        if action_text[-1] not in [".", "?", "!"]:
            action_text = action_text + "."

        return action_text

    def _stripAIText(self, inputText):
        # If for some reason '<|endoftext|>' is in the front of the text.
        inputText = inputText.lstrip()
        if inputText.find("<|endoftext|>") == 0:
            inputText = inputText[len("<|endoftext|>") + 1:]

        # First lets fix any weird punctuation.
        inputText = inputText.replace("’", "'")
        inputText = inputText.replace("`", "'")
        inputText = inputText.replace("“", '"')
        inputText = inputText.replace("”", '"')

        # Find the last sentence
        lastIndex = max(inputText.rfind("."), inputText.rfind("!"),
                        inputText.rfind("?"))

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

        # Remove trailing actions that don't have ">" in front.
        lines = inputText.split("\n")
        lastLine = lines[-1]
        if ("you ask" in lastLine or "You ask" in lastLine or "you say"
                in lastLine or "You say" in lastLine) and len(lines) > 1:
            inputText = "\n".join(lines[0:-1])

        # Remove trailing quotes
        numQuotes = inputText.count('"')
        if numQuotes % 2 != 0:
            finalInd = inputText.rfind('"')
            inputText = inputText[:finalInd]

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
        userText = self._prepareAction(inputStr)
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
