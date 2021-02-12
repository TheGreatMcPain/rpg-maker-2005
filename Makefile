SHELL=/bin/sh

VENV_NAME=virtualenv

TARGET=tensorflow-test.py

# Setup python virtualenv and install requirements
setup:
	python3 -m venv $(VENV_NAME); \
	. ./$(VENV_NAME)/bin/activate; \
	pip install -r requirements.txt; \
	deactivate

# Run TARGET
run:
	. ./$(VENV_NAME)/bin/activate; \
	python3 $(TARGET); \
	deactivate

# Delete files
clean:
	rm -rv __pycache__; \
	rm -rv $(VENV_NAME)
