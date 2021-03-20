SHELL=/bin/sh

# Setup python virtualenv and install requirements
setup:
	./setup.sh setup

# Delete files
clean:
	./setup.sh clean

# Install jedi, yapf, and pylint for auto-completion, code formatting, and linting
setup-development-stuff:
	./setup.sh setup_development_stuff
