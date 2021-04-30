# ChooseYourStory.com WebScraper (for training data collection)

The `cys-scraper.py` python script is a program that uses Selenium to grab test-based adventure games from [chooseyourstory.com](chooseyourstory.com).

The `storydata-to-text.py` python script is designed to read the JSON data that `cys-scraper.py` produces and creates a text file that will be used to fine-tune the GPT-2 language model.

## Setup

See: [rpg-maker-2005/README.md](../../README.md#setup)

## Usage

See each program's help message for details on each parameter, but the general idea is this.

```
$ ./cys-scraper.py -s <story ids> <other parameters> -o <output.json>
```

and

```
$ ./storydata-to-text.py <other parameters> -i <input.json> -o <output.txt>
```
