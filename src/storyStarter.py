''' This class handles premade prompts stored in a json file
    getPrompt takes in a genre, character name, and character class and returns a string that can be fed to the model
        The script will then chose random items and prompts from the sets contained under the genre and character class

    addPrompt adds data to the json file given the genre, and class that should be edited/added, and the sets of data that will be chosen from

    listGenres lists the available genres
    listClasses lists the available classes given the genre.
'''
import random
import json
import os


class StoryStarter:
    def __init__(self, starterJsonStr: str):
        self.prmoptDatabase = {}
        self.starterJson = os.path.abspath(starterJsonStr)

        if os.path.isfile(self.starterJson):
            with open(self.starterJson, 'r') as jsonFile:
                self.promptDatabase = json.load(jsonFile)

        jsonFile.close()

    ''' Returns a string based off of the premade story prompts that can be fed into the model to start an adventure!
        getPrompt(genre, character_name, character_class)
        randomly choses from the lists of data in the json file under the set genre and character class.
    '''

    def getPrompt(self, genre: str, charName: str, charClass: str):
        genreDatabase = self.promptDatabase[genre]
        classDatabase = genreDatabase[charClass]
        item1 = random.choice(classDatabase["item1"])
        item2 = random.choice(classDatabase["item2"])
        prompt = random.choice(classDatabase["prompt"])

        storyString = "You are " + charName + ", a " + charClass + ". "
        storyString += "You have a " + item1 + " and a " + item2 + ".\n\n"
        storyString += prompt

        return storyString

    ''' Edits the json file given the parameters:
        genre to be added/edited
        characterClass to be added/edited
        the set of the first items that could be randomly chosen to be added to the class' items
        the set of the second items that could be randomly chosen to be added to the class' items
        the set of prompts that could be randomly chosen to be added to he class' prompts
    '''

    def addPrompt(self, genre: str, charClass: str, items1: set, items2: set,
                  prompts: set):
        if genre not in self.promptDatabase:
            self.promptDatabase[genre] = {}
        genreDatabase = self.promptDatabase[genre]

        if charClass not in genreDatabase:
            genreDatabase[charClass] = {}
        classDatabase = genreDatabase[charClass]

        if "item1" not in classDatabase:
            classDatabase["item1"] = []
        classDatabase["item1"] = list(
            set(classDatabase["item1"]).union(items1))

        if "item2" not in classDatabase:
            classDatabase["item2"] = []
        classDatabase["item2"] = list(
            set(classDatabase["item2"]).union(items2))

        if "prompt" not in classDatabase:
            classDatabase["prompt"] = []
        classDatabase["prompt"] = list(
            set(classDatabase["prompt"]).union(prompts))

        with open(self.starterJson, 'w') as jsonFile:
            json.dump(self.promptDatabase, jsonFile, indent=2)

        jsonFile.close()

    #Returns a list of the available genres
    def listGenres(self):
        return list(self.promptDatabase.keys())

    #Returns a list of the available character classes given the genre
    def listClasses(self, genre: str):
        return list(self.promptDatabase[genre].keys())
