#!/bin/sh
# Simply a short cut to enable the virtual environment.
# Simply run ". ./start-virtualenv.sh"

echo $0

# Not exactly portable POSIX, but it should work on
# most systems
script_location=$(dirname $0)

. "$script_location/virtualenv/bin/activate"
