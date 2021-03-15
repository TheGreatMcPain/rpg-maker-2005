SHELL=/bin/sh

VENV_NAME=virtualenv

# Setup python virtualenv and install requirements
setup:
	python3 -m venv $(VENV_NAME); \
	. ./$(VENV_NAME)/bin/activate; \
	pip install -r requirements.txt; \
	pip install -r gpt-2/requirements.txt; \
	pip install tensorflow==2.4.1; \
	deactivate

# Delete files
clean:
	rm -rv __pycache__; \
	rm -rv $(VENV_NAME)

# Install jedi, yapf, and pylint for auto-completion, code formatting, and linting
setup-development-stuff:
	. ./$(VENV_NAME)/bin/activate; \
	pip install jedi yapf pylint; \
	deactivate
