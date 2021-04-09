import textwrap
import os
import sys
import time
import random

screen_width = 100


# Player Setup #
class player:
    def __init__(self):
        self.name = ""


player1 = player()

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
    #Prints the pretty title.
    print('RPGMaker2005 presents')
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
    question1 = "Hello, what is your name?\n"
    for character in question1:
        #This will occur throughout the intro code.  It allows the string to be typed gradually - like a typerwriter effect.
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.05)
    player_name = input("> ")
    player1.name = player_name

    #Obtains the player's choice.
    question2 = "Choose a number.....\n"
    for character in question2:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.05)

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


title_screen()
