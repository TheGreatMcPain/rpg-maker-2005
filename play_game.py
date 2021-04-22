#!/usr/bin/env python
# import textwrap
# import random
from google_drive_downloader import GoogleDriveDownloader as gdd
import os
import sys
import time
import threading
import argparse

from src import intro, story_manager, game, model_manager

# Initial Setup #

MODEL_DIR = "gpt2-model"
MODEL_NAME = "rpg_model"

DATA_PATH = "game_data"
TRANSCRIPT_PATH = os.path.join(DATA_PATH, "transcripts")
SAVESPATH = os.path.join(DATA_PATH, "saves")
STORY_JSON = os.path.join(DATA_PATH, "storyDatabase.json")

parser = argparse.ArgumentParser("Play NotAnother AIDungeon")
parser.add_argument("--gpu",
                    action="store_true",
                    help="Allow use of CUDA (CPU is default)")
parser.set_defaults(gpu=False)
args = parser.parse_args()

# Model downloader


def download_model(destination_folder: str):
    filename = "rpg_model.zip"
    destination_path = os.path.join(destination_folder, filename)

    # Check if destination_folder exists, and if it has files.
    if os.path.isdir(destination_folder):
        if len(os.listdir(destination_folder)) != 0:
            exists_message = "Model folder {}".format(destination_folder)
            exists_message += " already has stuff (skipping download)"
            print(exists_message)
            return

    # Download the model from GDrive
    download_message = "Downloading and extracting GPT-2 model. "
    download_message += "It's 1GB so it'll take a while.\n"
    print(download_message)
    gdd.download_file_from_google_drive(
        file_id="12bakAV7atjWwdKEPwFAZBfHnsIuLMqM2",
        dest_path=destination_path,
        showsize=True,
        unzip=True)

    # Remove the file when finished extracting.
    print("\nFinished extracting we'll now delete: {}\n".format(
        destination_path))
    os.remove(destination_path)


# AI text printer #


# Prepares a string do that words don't split in the terminal window.
def prevent_word_split(string: str, terminal_width: int):
    lines = string.split("\n")
    outString = ""
    for line in lines:
        words = line.split(" ")
        tempString = ""
        for word in words:
            tempString += "{} ".format(word)

            if len(tempString) >= terminal_width:
                tempString = tempString.rstrip()
                lastWord = tempString.split(" ")[-1]
                tempString = tempString[:len(tempString) -
                                        len(lastWord)] + "\n" + lastWord
                outString += tempString + " "
                tempString = ""

        outString += tempString.rstrip() + "\n"
    return outString


# Thinking Indicator #

# We'll use this to stop the thinking_indicator thread.
thinking_indicator_is_running = False


# This will be used in a thread for showing if the AI is thinking.
def thinking_indicator():
    global thinking_indicator_is_running
    thinking = ['|', '/', '-', '\\']
    string_length = len("\rThe AI is thinking {}".format(thinking[0]))
    while thinking_indicator_is_running:
        for think in thinking:
            print("\rThe AI is thinking {}".format(think), end="")
            time.sleep(0.25)
    # Clears the text
    print("\r{}".format(" " * string_length), end="\r")


# Title Screen #


def title_screen_options(Game: game.Game):
    #Allows the player to select the menu options, case-insensitive.
    option = input("> ")
    if option.lower() == ("play"):
        setup_game(Game)
    elif option.lower() == ("quit"):
        sys.exit()
    elif option.lower() == ("help"):
        help_menu(Game)
    while option.lower() not in ['play', 'help', 'quit']:
        print("Invalid command, please try again.")
        option = input("> ")
        if option.lower() == ("play"):
            setup_game(Game)
        elif option.lower() == ("quit"):
            sys.exit()
        elif option.lower() == ("help"):
            help_menu(Game)


def title_screen(Game: game.Game):
    #Clears the terminal of prior code for a properly formatted title screen.
    os.system('clear')
    time.sleep(0.5)  # Add a pause to make the intro less jarring.
    #Prints the pretty title.
    # print('RPGMaker2005 presents')
    intro.showIntro()
    print("")
    print("    Play    ")
    print("    Help    ")
    print("    Quit    ")
    title_screen_options(Game)


# Help Menu #


def help_menu(Game: game.Game):
    print(Game.help())
    title_screen_options(Game)


# Execute Game #
def setup_game(Game: game.Game):
    #Clears the terminal for the game to start.
    os.system('clear')
    #Obtains the player's name.
    question1 = "What is your character's name?"
    intro.slowPrint(question1, 10, 25, True)
    player_name = input("> ")

    #Obtains the player's choice.
    question2 = "Choose a genre..."
    intro.slowPrint(question2, 10, 25, True)

    # Genre/Class selection menu
    list_of_options = {}
    listOfGenres = Game.storyStarter.listGenres()
    for x in range(len(listOfGenres)):
        list_of_options[str(x)] = listOfGenres[x]
        message = "{}: {}".format(x, listOfGenres[x])
        intro.slowPrint(message, 10, 25, True)
    genre_setting = input("> ")

    if genre_setting in list_of_options.keys():
        genre_setting = list_of_options[genre_setting]

    intro.slowPrint("Choose a class...", 10, 25, True)

    list_of_options = {}
    listOfClasses = Game.storyStarter.listClasses(genre_setting)
    for x in range(len(listOfClasses)):
        list_of_options[str(x)] = listOfClasses[x]
        message = "{}: {}".format(x, listOfClasses[x])
        intro.slowPrint(message, 10, 25, True)
    class_setting = input("> ")

    if class_setting in list_of_options.keys():
        class_setting = list_of_options[class_setting]

    # os.system('clear')
    print("# Here begins the adventure... #")

    Game.startGame(genre_setting, player_name, class_setting)

    while Game.keepGoing:
        message = prevent_word_split(Game.currentText,
                                     os.get_terminal_size()[0])
        intro.slowPrint(message, 10, 25, True)

        userInput = input("> ")

        global thinking_indicator_is_running
        thinking_indicator_is_running = True
        thinkingThread = threading.Thread(target=thinking_indicator)

        # Start thinking indicator
        thinkingThread.start()

        Game.gameCommand(userInput)

        # Stop thinking indicator
        thinking_indicator_is_running = False
        # Wait for thinking_indicator to stop
        thinkingThread.join()


if __name__ == "__main__":
    # We must first download the model
    download_model("gpt2-model/rpg_model")

    modelManager = model_manager.ModelManager(MODEL_DIR,
                                              MODEL_NAME,
                                              allow_gpu=args.gpu)
    Game = game.Game(modelManager, TRANSCRIPT_PATH, SAVESPATH, STORY_JSON)

    title_screen(Game)
