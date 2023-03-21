# NotAnother AIDungeon: An AI powered text-based RPG

## Setup

1. Clone the repository (Also clones GPT2 submodule)

```
$ git clone --recursive <repo url>
```

2. Setup git-annex to download the GPT2 model. (Requires git-annex to be installed.)

Since storing large binary files is not ideal for git the GPT2 model has been stored via git-annex.

```
$ git annex init

$ git annex sync

$ git annex sync --content
```

_Originally `play.py` would just download the model from GDrive, but the python module we were using for that has stopped working._

3. Setup the pyton environment and install dependencies

```
$ ./setup.sh setup
```

If you already have TensorFlow 2.x.x (2.4.1 as of writing). You can use this command instead.

```
$ ./setup.sh setup_system_tensorflow
```

4. Activate the python environment

```
$ . ./start-virtualenv.sh
```

5. Play

```
$ python ./play_game.py
```

# Below is Dev Stuff

## Useful git commands (run these while inside the repository)

### Set your username and email.

To set it globally just add the `--global` flag right after `git config`.

```
$ git config user.name "<insert your name>"

$ git config user.email "<insert email>"
```

### Have git save your credentials in `~/.git-credentials`, so you don't have to enter your name and password all the time.

#### WARNING!!! This will store the password in plain text.

```
$ git config credential.helper store
```
