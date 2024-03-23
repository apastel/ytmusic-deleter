#!/bin/bash

# Validate argument
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <major|minor|patch>"
  exit 1
fi

if [[ "$1" != "major" && "$1" != "minor" && "$1" != "patch" ]]; then
  echo "Invalid argument: Must be 'major', 'minor', or 'patch'."
  exit 1
fi

# Array of files with version numbers
files=(
  "pyproject.toml"
  "app/pyproject.toml"
  "app/src/build/settings/base.json"
  "cli/pyproject.toml"
)

# Function to bump version
bump_version_toml() {
  local file=$1
  local version_part=$2

  # Extract current version (limit to 1 match)
  current_version=$(grep -m 1 "version =" "$file" | cut -d\" -f2)
  major=$(echo "$current_version" | cut -d. -f1)
  minor=$(echo "$current_version" | cut -d. -f2)
  patch=$(echo "$current_version" | cut -d. -f3)

  # Bump the specified version part
  case "$version_part" in
    major) major=$((major + 1)); minor=0; patch=0;;
    minor) minor=$((minor + 1)); patch=0;;
    patch) patch=$((patch + 1));;
  esac

  # Create new version string
  new_version="${major}.${minor}.${patch}"

  # Replace old version with new version in the file
  sed -i "s/version = \"$current_version\"/version = \"$new_version\"/" "$file"
}

# Function to bump version in JSON
bump_version_json() {
  local file=$1
  local version_part=$2

  # Backup original file
  cp "$file" "$file.bak"

  # Read the file content
  content=$(cat "$file")

  # Extract current version with a bit more control
  current_version=$(echo "$content" | grep -m 1 '"version":' | cut -d: -f2 | tr -d ' ",' | head -n 1)
  major=$(echo "$current_version" | cut -d. -f1)
  minor=$(echo "$current_version" | cut -d. -f2)
  patch=$(echo "$current_version" | cut -d. -f3)

  # Bump the specified version part
  case "$version_part" in
    major) major=$((major + 1)); minor=0; patch=0;;
    minor) minor=$((minor + 1)); patch=0;;
    patch) patch=$((patch + 1));;
  esac


  # Create new version string
  new_version="${major}.${minor}.${patch}"

  # Replace old version with new version in a temporary string
  updated_content=$(echo "$content" | sed "s/\"version\": \"$current_version\"/\"version\": \"$new_version\"/")

  # Write the updated content to the file
  echo "$updated_content" > "$file"

  # Remove the backup if successful
  rm -f "$file.bak"
}

# Iterate over files and bump version
for file in "${files[@]}"; do
  if [[ "${file##*.}" == "toml" ]]; then
    bump_version_toml "$file" "$1"
  else
    bump_version_json "$file" "$1"
  fi
done

echo "Complete. Check files for successful version bump."
