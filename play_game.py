#!/usr/bin/env python
import textwrap
from google_drive_downloader import GoogleDriveDownloader as gdd
import os
import sys
import time
import threading
import argparse
import json
import hashlib

from src import ui_utils, story_manager, game, model_manager

# Initial Setup #

# Global variables
MODEL_DIR = "gpt2-model"
MODEL_NAME = "rpg_model"

DATA_PATH = "game_data"
TRANSCRIPT_PATH = os.path.join(DATA_PATH, "transcripts")
SAVESPATH = os.path.join(DATA_PATH, "saves")
STORY_JSON = os.path.join(DATA_PATH, "storyDatabase.json")

# Argument parser
parser = argparse.ArgumentParser("Play NotAnother AIDungeon")
parser.add_argument("--gpu",
                    action="store_true",
                    help="Allow use of CUDA (CPU is default)")
parser.add_argument("--disable_slow_print",
                    dest="enable_slow_print",
                    action="store_false",
                    help="Disable (print as if someone was typing)")
parser.add_argument("--update-model",
                    dest="update_model",
                    action="store_true",
                    help="Updates the GPT2 model if it's not up-to-date.")
parser.set_defaults(gpu=False)
parser.set_defaults(enable_slow_print=True)
parser.set_defaults(update_model=False)
args = parser.parse_args()

# Utilities #


def hashes_match(hashes_data1: dict, hashes_data2: dict):
    for file in hashes_data1.keys():
        hash1 = hashes_data1[file]
        if file not in hashes_data2.keys():
            return False

        hash2 = hashes_data2[file]
        if hash1 != hash2:
            return False

    return True


def get_local_model_hashes(model_path: str):
    os.listdir(model_path)
    hashes = {}
    for file in os.listdir(model_path):
        file_path = os.path.join(model_path, file)
        blake2b_hash = hashlib.blake2b()
        with open(file_path, "rb") as f:
            chunk = f.read(8192)
            while chunk:
                blake2b_hash.update(chunk)
                chunk = f.read(8192)
        hashes[file] = blake2b_hash.hexdigest()
    return hashes


def get_model_hashes_from_gdrive(destination_folder: str):
    filename = "rpg-model_black2b.json"
    destination_path = os.path.join(destination_folder, filename)

    # Download the hashes json file
    gdd.download_file_from_google_drive(
        file_id="1-gHJZcBi8WQMtljydjHXiVkqa-0PfjNL",
        dest_path=destination_path)

    # Load the json file and return the object.
    hashes = get_json(destination_path)

    # Delete the downloaded file
    print("Finished loading json data deleting: {}".format(destination_path))
    os.remove(destination_path)

    return hashes


def is_model_outofdate(model_dir: str):
    remote_hashes = get_model_hashes_from_gdrive("./")
    local_hashes = get_local_model_hashes(model_dir)

    return hashes_match(local_hashes, remote_hashes)


def download_model(destination_folder: str, update: bool = False):
    filename = "rpg_model.zip"
    destination_path = os.path.join(destination_folder, filename)

    # Check if destination_folder exists, and if it has files.
    if os.path.isdir(destination_folder):
        if len(os.listdir(destination_folder)) != 0:
            if update:
                print("Checking for model updates...")
                if not is_model_outofdate(destination_folder):
                    print("Model is out-of-date. Updating...")

                    # Delete files in destination_folder
                    for file in os.listdir(destination_folder):
                        file_path = os.path.join(destination_folder, file)
                        os.remove(file_path)
                else:
                    print("Model is up-to-date...")
                    return
            else:
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


# Use textwrap to prevent text from becoming too long.
def wrap_text(string: str, terminal_width: int):
    output_lines = []
    lines = string.split("\n")

    for line in lines:
        if len(line) <= terminal_width:
            output_lines.append(line)
            continue

        output_lines += textwrap.wrap(line,
                                      width=terminal_width,
                                      replace_whitespace=False)

    return "\n".join(output_lines)


# Universal way to clear the screen.
def clear_screen(numlines: int = 100):
    if os.name == "posix":
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        os.system("CLS")
    else:
        # Fallback for other platforms
        print("\n" * numlines)


# Although I think the 'slowPrint' function from ui_utils
# is visually appealing I think there should be an option to
# turn it off.
# This function will just make implementing this option more
# easier.
def slow_print(enable: bool, input_string: str, range1: int, range2: int,
               newline: bool):
    if enable:
        ui_utils.slowPrint(input_string, range1, range2, newline)
    else:
        end = ""
        if newline:
            end = "\n"
        print(input_string, end=end)


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
    slow_print(
        args.enable_slow_print,
        'Load from Save? (y)es or (n)o (blank will also count as "no")', 25,
        50, True)
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
        slow_print(args.enable_slow_print, "Select a save by number", 25, 50,
                   True)
        for i in range(len(saves)):
            save = saves[i]

            message = "{}: ".format(i + 1)
            message += "File: {} ".format(save['fileName'])
            message += "Genre: {} ".format(save['genre'])
            message += "Class: {} ".format(save['class'])
            message += "Player Name: {}\n".format(save['player'])

            slow_print(args.enable_slow_print, message, 25, 50, False)

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
        slow_print(args.enable_slow_print, "What is your character's name?",
                   25, 50, True)
        player_name = input("> ")

        #Obtains the player's choice.
        slow_print(args.enable_slow_print, "Choose a genre...", 25, 50, True)

        # Genre/Class selection menu
        list_of_options = {}
        list_of_genres = game.storyStarter.listGenres()
        list_of_genres += ['custom']
        for x in range(len(list_of_genres)):
            option_num = x + 1
            list_of_options[str(option_num)] = list_of_genres[x]
            message = "{}: {}".format(option_num, list_of_genres[x])
            slow_print(args.enable_slow_print, message, 25, 50, True)
        genre_setting = input("Pick a number> ")

        if genre_setting in list_of_options.keys():
            genre_setting = list_of_options[genre_setting]

        if genre_setting == "custom":
            message = "Please write a custom prompt. "
            message += "(When done writing type '/done')\n"
            message += "When writting a prompt it should include as much\n"
            message += "detail as possible to help the AI.\n\n"
            message += "Here is an example...\n\n"
            message += "prompt> You are Karl who is a Knight in the kingdom of Ironwood.\n"
            message += "prompt>\n"
            message += "prompt> The King of Ironwood has asked you to investigate recent\n"
            message += "prompt> dragon attacks in the nearby villages.\n"
            message += "prompt>\n"
            message += "prompt> You and your fellow knights arrive at a village that\n"
            message += "prompt> has been reduced to ash by the dragon.\n"
            slow_print(args.enable_slow_print, message, 25, 50, True)

            # Allow the user to add '\n' to their prompt.
            custom_prompt = ""
            while True:
                cur_input = input("prompt> ")
                if cur_input.lower() == "/done":
                    break
                custom_prompt += cur_input + "\n"

            # Make sure the prompt doesn't have any trailing whitespace.
            custom_prompt = custom_prompt.strip()

            class_setting = "custom"
            game.startGame(genre_setting,
                           player_name,
                           class_setting,
                           customPrompt=custom_prompt)
        else:
            slow_print(args.enable_slow_print, "Choose a class...", 25, 50,
                       True)

            list_of_options = {}
            list_of_classes = game.storyStarter.listClasses(genre_setting)
            for x in range(len(list_of_classes)):
                option_num = x + 1
                list_of_options[str(option_num)] = list_of_classes[x]
                message = "{}: {}".format(option_num, list_of_classes[x])
                slow_print(args.enable_slow_print, message, 25, 50, True)
            class_setting = input("Pick a number> ")

            if class_setting in list_of_options.keys():
                class_setting = list_of_options[class_setting]

            game.startGame(genre_setting, player_name, class_setting)

    while game.keepGoing:
        terminal_width = 80
        if os.get_terminal_size()[0] < 90:
            terminal_width = os.get_terminal_size()[0] - 10

        message = wrap_text(game.currentText, terminal_width)
        slow_print(args.enable_slow_print, message, 50, 75, True)

        user_input = input("> ").strip()

        if len(user_input) > 0:
            if user_input[0] != "/":
                # Replace the printed user text with the one
                # which will be used by the AI model.
                new_input = game.prepareAction(user_input)
                padding = " " * len("> " + user_input)

                # Move cursor up a line and clear the text with 'padding'
                print("\033[F\r" + padding, end="\r")
                # print the new text in it's place.
                print("> " + new_input)

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
    download_model("gpt2-model/rpg_model", args.update_model)

    model_manager = model_manager.ModelManager(MODEL_DIR,
                                               MODEL_NAME,
                                               allowGpu=args.gpu)
    game = game.Game(model_manager, TRANSCRIPT_PATH, SAVESPATH, STORY_JSON)

    title_screen(game)
