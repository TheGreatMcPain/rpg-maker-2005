''' Some functions to be put into the game class
'''

def help():
    print("After each prompt type a command, for example: ")
    print("> go to the town\n")
    print("For dialouge use double quotes (\"), for example: ")
    print("> \"hello\" \n")
    print("To type a command, type \"/\" in front of the command")
    print("Available Commands:")
    print("help - Displays a list of commands")
    print("quit - quits the adventure")
    print("transcript - saves the adventure to a file")
    print("remember - marks the last action as important")
    print("retry - send the last action back into the bot")

def quitGame():
    quit = True

def remember(action: dict):
    StoryManager.saveAction(action)

def transcript(fileName: str):
    if lower(fileName[-4:]) != ".txt":
        fileName += ".txt"

    with open(fileName, 'w') as transcriptFile:
        transcriptFile.write(StoryManager.getTranscript())

def retry(action: dict):
    userText = action["userText"]
    aiText = ModelManager.getSampleFromText(userText)
    newAction = StoryManager.createAction(aiText, userText)

    return newAction
