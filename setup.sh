#!/bin/sh

VENV_NAME=virtualenv
BIN="$VENV_NAME/bin"

activate_env() {
  if [ -d "$VENV_NAME/Scripts" ]; then
    BIN="$VENV_NAME/Scripts"
  fi

  . ./$BIN/activate
}

setup() {
  python3 -m venv $VENV_NAME

  activate_env

  pip install -r requirements.txt
  pip install -r gpt-2/requirements.txt
  pip install tensorflow==2.4.1

  deactivate
}

clean() {
  rm -rv __pycache__
  rm -rv $VENV_NAME
}

setup_development_stuff() {
  activate_env

  pip install jedi yapf pylint neovim

  deactivate
}

if [ "$1"x = "setup"x ]; then
  setup
elif [ "$1"x = "clean"x ]; then
  clean
elif [ "$1"x = "setup_development_stuff"x ]; then
  setup_development_stuff
fi
