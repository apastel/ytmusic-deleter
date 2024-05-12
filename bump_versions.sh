#!/bin/bash

# Validate argument
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <major|minor|patch|custom_version>"
  exit 1
fi

if [[ "$1" != "major" && "$1" != "minor" && "$1" != "patch" ]]; then
  echo "Custom version supplied: '$1'"
fi

# Array of files with version numbers
files=(
  "ytmusic_deleter/_version.py"
  "gui/src/build/settings/base.json"
)

# Function to bump version
bump_version_py() {
  local file=$1
  local version_part=$2

  # Extract current version (limit to 1 match)
  current_version=$(grep -m 1 "__version__ =" "$file" | cut -d\" -f2)
  major=$(echo "$current_version" | cut -d. -f1)
  minor=$(echo "$current_version" | cut -d. -f2)
  patch=$(echo "$current_version" | cut -d. -f3)

if [[ "$version_part" != "major" && "$version_part" != "minor" && "$version_part" != "patch" ]]; then
  new_version="$version_part"
else
  # Bump the specified version part
  case "$version_part" in
    major) major=$((major + 1)); minor=0; patch=0;;
    minor) minor=$((minor + 1)); patch=0;;
    patch) patch=$((patch + 1));;
  esac

  # Create new version string
  new_version="${major}.${minor}.${patch}"
fi

  # Replace old version with new version in the file
  sed -i "s/__version__ = \"$current_version\"/__version__ = \"$new_version\"/" "$file"
  echo "Bumped \"$file\" from \"$current_version\" to \"$new_version\""
}

# Function to bump version in JSON
bump_version_json() {
  local file=$1
  local version_part=$2

  # Read the file content
  content=$(cat "$file")

  # Extract current version with a bit more control
  current_version=$(echo "$content" | grep -m 1 '"version":' | cut -d: -f2 | tr -d ' ",' | head -n 1)
  major=$(echo "$current_version" | cut -d. -f1)
  minor=$(echo "$current_version" | cut -d. -f2)
  patch=$(echo "$current_version" | cut -d. -f3)

  if [[ "$version_part" != "major" && "$version_part" != "minor" && "$version_part" != "patch" ]]; then
    new_version="$version_part"
  else
    # Bump the specified version part
    case "$version_part" in
      major) major=$((major + 1)); minor=0; patch=0;;
      minor) minor=$((minor + 1)); patch=0;;
      patch) patch=$((patch + 1));;
    esac

    # Create new version string
    new_version="${major}.${minor}.${patch}"
  fi

  # Replace old version with new version in a temporary string
  updated_content=$(echo "$content" | sed "s/\"version\": \"$current_version\"/\"version\": \"$new_version\"/")

  # Write the updated content to the file
  echo "$updated_content" > "$file"
  echo "Bumped \"$file\" from \"$current_version\" to \"$new_version\""
}

# Iterate over files and bump version
for file in "${files[@]}"; do
  if [[ "${file##*.}" == "py" ]]; then
    bump_version_py "$file" "$1"
  else
    bump_version_json "$file" "$1"
  fi
done

echo "Complete. Check files for successful version bump."
