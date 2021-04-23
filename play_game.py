#!/usr/bin/env python
# import textwrap
# import random
from google_drive_downloader import GoogleDriveDownloader as gdd
import os
import sys
import time
import threading
import argparse
import json

from src import ui_utils, story_manager, game, model_manager

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

# Utilities #


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


# Restricts line length when printing.
def prevent_word_split(string: str, terminal_width: int):
    last_new_line = 0
    for i in range(len(string)):
        if string[i] == "\n":
            last_new_line = 0
        elif last_new_line > terminal_width and string[i] == " ":
            string = string[:i] + "\n" + string[i:]
            last_new_line = 0
        else:
            last_new_line += 1
    return string


# Universal way to clear the screen.
def clear_screen(numlines: int = 100):
    if os.name == "posix":
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        os.system("CLS")
    else:
        # Fallback for other platforms
        print("\n" * numlines)


# get info from json
def get_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


# get game saves. (List of saves and some info from them)
def get_game_saves(saves_path):
    saves = [
        x for x in os.listdir(saves_path) if x.split(".")[-1].lower() == "json"
    ]
    if len(saves) == 0:
        return False

    saves_info = []
    for save in saves:
        save_info = {}
        save_location = os.path.join(saves_path, save)
        save_data = get_json(save_location)

        save_info['filePath'] = save_location
        save_info['fileName'] = save.split(".json")[0]
        save_info['genre'] = save_data['genre']
        save_info['class'] = save_data['class']
        save_info['player'] = save_data['player']

        saves_info.append(save_info)
    return saves_info


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


def title_screen_options(game: game.Game):
    #Allows the player to select the menu options, case-insensitive.
    option = input("> ")
    if option.lower() == ("play"):
        setup_game(game)
    elif option.lower() == ("quit"):
        sys.exit()
    elif option.lower() == ("help"):
        help_menu(game)
    while option.lower() not in ['play', 'help', 'quit']:
        print("Invalid command, please try again.")
        option = input("> ")
        if option.lower() == ("play"):
            setup_game(game)
        elif option.lower() == ("quit"):
            sys.exit()
        elif option.lower() == ("help"):
            help_menu(game)


def title_screen(game: game.Game):
    # Clears the terminal of prior code for a properly formatted title screen.
    clear_screen()
    time.sleep(0.75)  # Add a pause to make the intro less jarring.
    # Prints the pretty title.
    # print('RPGMaker2005 presents')
    ui_utils.showIntro()
    print("")
    print("    Play    ")
    print("    Help    ")
    print("    Quit    ")
    title_screen_options(game)


# Help Menu #


def help_menu(game: game.Game):
    print(game.help())
    title_screen_options(game)


# Execute Game #
def setup_game(game: game.Game):
    # Ask if player wants to load from save.
    ui_utils.slowPrint(
        'Load from Save? (y)es or (n)o (blank will also count as "no")', 10,
        25, True)
    load_save = input("> ").strip().lower()
    if len(load_save) > 0:
        while load_save not in ("yes", "no", "y", "n"):
            print("Invalid option please try again.")
            load_save = input("> ").strip()

    if load_save in ("yes", "y"):
        # Display save options
        saves = get_game_saves(SAVESPATH)
        if saves == False:
            print("There are no saves! exiting...")
            sys.exit(1)
        save_options = {}
        ui_utils.slowPrint("Select a save by number", 10, 25, True)
        for i in range(len(saves)):
            save = saves[i]

            message = "{}: ".format(i + 1)
            message += "File: {} ".format(save['fileName'])
            message += "Genre: {} ".format(save['genre'])
            message += "Class: {} ".format(save['class'])
            message += "Player Name: {}\n".format(save['player'])

            ui_utils.slowPrint(message, 10, 25, True)

            save_options[str(i + 1)] = save['filePath']

        user_option = input("> ").strip()

        while user_option not in save_options.keys():
            print("Invalid option please try again.")
            user_option = input("> ").strip()

        # Once selected get the save filePath and load it via StoryManager.
        save_path = save_options[user_option]
        if not game.storyManager.loadStoryData(save_path):
            print("Failed to load save file! exiting...")
            sys.exit(1)

        # Resume game by printing the current transcript
        print(game.resumeGame())
    else:
        #Obtains the player's name.
        ui_utils.slowPrint("What is your character's name?", 10, 25, True)
        player_name = input("> ")

        #Obtains the player's choice.
        ui_utils.slowPrint("Choose a genre...", 10, 25, True)

        # Genre/Class selection menu
        list_of_options = {}
        list_of_genres = game.storyStarter.listGenres()
        for x in range(len(list_of_genres)):
            option_num = x + 1
            list_of_options[str(option_num)] = list_of_genres[x]
            message = "{}: {}".format(option_num, list_of_genres[x])
            ui_utils.slowPrint(message, 10, 25, True)
        genre_setting = input("> ")

        if genre_setting in list_of_options.keys():
            genre_setting = list_of_options[genre_setting]

        ui_utils.slowPrint("Choose a class...", 10, 25, True)

        list_of_options = {}
        list_of_classes = game.storyStarter.listClasses(genre_setting)
        for x in range(len(list_of_classes)):
            option_num = x + 1
            list_of_options[str(option_num)] = list_of_classes[x]
            message = "{}: {}".format(option_num, list_of_classes[x])
            ui_utils.slowPrint(message, 10, 25, True)
        class_setting = input("> ")

        if class_setting in list_of_options.keys():
            class_setting = list_of_options[class_setting]

        game.startGame(genre_setting, player_name, class_setting)

    while game.keepGoing:
        terminal_width = 80
        if os.get_terminal_size()[0] < 90:
            terminal_width = os.get_terminal_size()[0] - 10

        message = prevent_word_split(game.currentText, terminal_width)
        ui_utils.slowPrint(message, 50, 75, True)

        user_input = input("> ")

        global thinking_indicator_is_running
        thinking_indicator_is_running = True
        thinking_thread = threading.Thread(target=thinking_indicator)

        # Start thinking indicator
        thinking_thread.start()

        game.gameCommand(user_input)

        # Stop thinking indicator
        thinking_indicator_is_running = False
        # Wait for thinking_indicator to stop
        thinking_thread.join()


if __name__ == "__main__":
    # We must first download the model
    download_model("gpt2-model/rpg_model")

    model_manager = model_manager.ModelManager(MODEL_DIR,
                                               MODEL_NAME,
                                               allow_gpu=args.gpu)
    game = game.Game(model_manager, TRANSCRIPT_PATH, SAVESPATH, STORY_JSON)

    title_screen(game)
