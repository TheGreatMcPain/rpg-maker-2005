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

# Adds '__init__.py' files into gpt_2 and gpt_2/src
# This allows gpt_2 python modules to act like a python package.
add_init_gpt2() {
  touch "$SCRIPT_LOCATION/gpt_2/__init__.py"
  touch "$SCRIPT_LOCATION/gpt_2/src/__init__.py"

  # Modify files in "gpt_2/src"
  sed "s|import model|from gpt_2.src import model|" \
    -i "$SCRIPT_LOCATION/gpt_2/src/sample.py"
}

# Initial setup
# This time use already installed packages on the system
# (If TensorFlow is installed via package-manager)
setup_system_tensorflow() {
  activate_env --system-site-packages
  add_init_gpt2

  pip install -r requirements.txt
  pip install -r gpt_2/requirements.txt
}

# Initial setup
setup() {
  activate_env
  add_init_gpt2

  pip install -r requirements.txt
  pip install -r gpt_2/requirements.txt
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
  add_init_gpt2

  pip install jedi yapf pylint neovim
}

# Parse argument
if [ "$1"x = "activate_env"x ]; then
  activate_env
elif [ "$1"x = "setup"x ]; then
  setup
elif [ "$1"x = "setup_system_tensorflow"x ]; then
  setup_system_tensorflow
elif [ "$1"x = "clean"x ]; then
  clean
elif [ "$1"x = "setup_development_stuff"x ]; then
  setup_development_stuff
fi
