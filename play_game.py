#!/usr/bin/env python
# import textwrap
# import random
from google_drive_downloader import GoogleDriveDownloader as gdd
import os
import sys
import time

# screen_width = 100

from src import intro, story_manager


# Player Setup #
class player:
    def __init__(self):
        self.name = ""


player1 = player()

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


# Title Screen #


def title_screen_options():
    #Allows the player to select the menu options, case-insensitive.
    option = input("> ")
    if option.lower() == ("play"):
        setup_game()
    elif option.lower() == ("quit"):
        sys.exit()
    elif option.lower() == ("help"):
        help_menu()
    while option.lower() not in ['play', 'help', 'quit']:
        print("Invalid command, please try again.")
        option = input("> ")
        if option.lower() == ("play"):
            setup_game()
        elif option.lower() == ("quit"):
            sys.exit()
        elif option.lower() == ("help"):
            help_menu()


def title_screen():
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
    title_screen_options()


# Help Menu #


def help_menu():
    print("")
    print("Type a basic form of verb")
    print("let you interact with this bot.\n")
    print("Please ensure to type in lowercase for ease.\n")
    print("    Please select an option to continue.     ")
    print('#' * 20)
    print("    Play    ")
    print("    Help    ")
    print("    Quit    ")
    title_screen_options()


# Execute Game #
def setup_game():
    #Clears the terminal for the game to start.
    os.system('clear')
    #Obtains the player's name.
    question1 = "Hello, what is your name?"
    intro.slowPrint(question1, 10, 25, True)
    # for character in question1:
    #     #This will occur throughout the intro code.  It allows the string to be typed gradually - like a typerwriter effect.
    #     sys.stdout.write(character)
    #     sys.stdout.flush()
    #     time.sleep(0.05)
    player_name = input("> ")
    player1.name = player_name

    #Obtains the player's choice.
    question2 = "Choose a number....."
    intro.slowPrint(question2, 10, 25, True)
    # for character in question2:
    #     sys.stdout.write(character)
    #     sys.stdout.flush()
    #     time.sleep(0.05)

    #Prints the guide for the player.
    print("1. Fantagy")
    print("2. Sic-fi")
    print("3. Zombi apocalypse")
    print("4. Or, write a custom pormpt")
    print("#####################################################")
    setting = input("> ")
    acceptable_setting = ['1', '2', '3', '4']

    while setting.lower() not in acceptable_setting:
        print("That is not an acceptable number, please try again.")
        setting = input("> ")
    player1.setting = setting.lower()

    os.system('clear')
    print("# Here begins the adventure... #")

    main_game_loop()


if __name__ == "__main__":
    # We must first download the model
    download_model("gpt2-model/rpg_model")

    # title_screen()
