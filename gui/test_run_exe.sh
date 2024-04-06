#!/bin/bash

# Check if a version argument is provided
if [ -z "$1" ]; then
  echo "Error: Please provide a version string as an argument."
  exit 1
fi

# Store the version argument
version_str="$1"

export QT_QPA_PLATFORM=offscreen 
output=$(timeout 10s pdm fbs run)

# Check if the output contains the specific CLI version
if grep -q "CLI version: $version_str" <<< "$output"; then
    echo "GUI is running the right CLI version: $version_str"
else
    echo "CLI version: $version_str not found in output, which is the following:"
    echo $output
    exit 1
fi
