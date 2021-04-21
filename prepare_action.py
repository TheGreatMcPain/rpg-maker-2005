import csv
import json
import re


def load_story(filename):
    with open(filename, "r") as fp:
        story = json.load(fp)
    return story

def prepare_action(story):
    user_action=input('')
    first_word = user_action.split(" ")[0]
    
    if first_word[0] == '"':
        action_text = "You say, " + user_action
    elif fisrt_word[0].isupper() == True:
        user_action.lower()
        action_text = "You " + user_action
    else:
        action_text = "You " + user_action

    return action_text
