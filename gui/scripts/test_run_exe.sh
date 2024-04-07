#!/bin/bash

# Check if a version argument is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a version string as an argument."
  exit 1
fi

# Store the version argument
version_str="$1"

# Makes app run headless
export QT_QPA_PLATFORM=offscreen

# Save the output of the app startup
output=$(timeout 10s pdm fbs run)

# Check if the output contains the right CLI version
if grep -q "CLI version: $version_str" <<< "$output"; then
    echo "GUI is running the right CLI version: $version_str"
else
    echo "CLI version: $version_str not found in output, which was the following:"
    echo $output
    exit 1
fi
