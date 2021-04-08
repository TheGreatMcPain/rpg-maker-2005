#!/bin/sh

VENV_NAME=virtualenv
# Not exactly portable, but it should work on
# most systems
SCRIPT_LOCATION=$(dirname $0)
BIN="$SCRIPT_LOCATION/$VENV_NAME/bin"

# Sets up and activates virtualenv
activate_env() {
  if ! [ -d "$SCRIPT_LOCATION/$VENV_NAME" ]; then
    if [ "$1"x = "--system-site-packages"x ]; then
      python3 -m venv "$SCRIPT_LOCATION/$VENV_NAME" --system-site-packages
    else
      python3 -m venv "$SCRIPT_LOCATION/$VENV_NAME"
    fi
  fi

  if [ -d "$SCRIPT_LOCATION/$VENV_NAME/Scripts" ]; then
    BIN="$SCRIPT_LOCATION/$VENV_NAME/Scripts"
  fi

  if [ -f ./$BIN/activate ]; then
    . ./$BIN/activate
  else
    exit 1
  fi
}

# Initial setup
# This time use already installed packages on the system
# (If TensorFlow is installed via package-manager)
setup_no_tensorflow() {
  activate_env --system-site-packages

  pip install -r requirements.txt
  pip install -r gpt-2/requirements.txt
}

# Initial setup
setup() {
  activate_env

  pip install -r requirements.txt
  pip install -r gpt-2/requirements.txt
  pip install tensorflow==2.4.1
}

# Delete __pycache__ and virtualenv
clean() {
  rm -rv __pycache__
  rm -rv "$SCRIPT_LOCATION/$VENV_NAME"
}

# Install needed things for James' NeoVim setup.
setup_development_stuff() {
  activate_env

  pip install jedi yapf pylint neovim
}

# Parse argument
if [ "$1"x = "activate_env"x ]; then
  activate_env
elif [ "$1"x = "setup"x ]; then
  setup
elif [ "$1"x = "setup_no_tensorflow"x ]; then
  setup_no_tensorflow
elif [ "$1"x = "clean"x ]; then
  clean
elif [ "$1"x = "setup_development_stuff"x ]; then
  setup_development_stuff
fi
