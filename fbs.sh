#!/bin/sh

# Change directory to the gui package
cd "$PDM_PROJECT_ROOT/gui" || exit 1

# Forward all arguments passed to the script (after the script name)
# to the fbs command
exec fbs "$@"
