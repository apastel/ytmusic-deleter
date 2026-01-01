# Developer's Guide
## Setup
* Clone the project
* `wget --content-disposition "https://drive.google.com/uc?export=download&id=10bFocvHsORN9_RugTqb2TrRW_UG2dCST"`

## Dev Container
This project uses Dev Containers to set up the development environment. Open the project in VS Code and use the Dev Containers
extension to open the project in the dev container. Upon completion, the YTMusic Deleter application should automatically start up in a
X11 GUI window.

>Note there may be some UI style quirks as this is running using X11 in a container but there shouldn't be any groundbreaking differences.
Might not be able to get `xdg-open` to work for opening the file manager location of your app data directory.

## Run
* `ytmusic-deleter` to run CLI
* `pdm fbs run` to run GUI

## Signing In
* See [README.md](./README.md#setup)

## Pytest
* `cp tests/resources/test.example.cfg tests/resources/test.cfg`
  * Fill out file
* `wget --content-disposition -P tests/resources/ "https://drive.google.com/uc?export=download&id=18AP7mQqQxqj2_delNyhoCNa6UCUCN9-P"`
  * This will download the sample mp3 for upload tests
* Copy `browser.json` from app data directory into `tests/resources`
* `pdm run pytest` or use VS Code Testing tab
* Any commit that touches the CLI [(i.e. anything in ytmusic_deleter/)](./ytmusic_deleter/) will automatically trigger the Pytest action on GitHub.

## Github Actions
* Run "Create Tag" to tag a new release from `main`
  * This will trigger "Release and Publish" on the tag which will:
    * Build and verify the Windows, Linux, and Mac installers
    * Build the PyPI distributable for the CLI version
    * Publish the dist to PyPI
    * Draft a new GitHub Release
    * NOT run Pytest because the HEAD commit should have already passed Pytest
* To build a test release for a branch:
  * Run "Release and Publish" on the branch
  * Select "Skip" for "Skip publishing this release to PyPI?"
* Once a week, "Update dependencies" will create a PR for any new PDM dependencies
  * This includes new versions of `ytmusicapi` which is important.
  * Close/re-open the PR to trigger the GitHub Actions checks

### Run Qt Designer
Qt Designer is how the UI dialogs are created.

* Activate .venv
* `pyside6-designer`
* After updating .ui resource file...
  * `pdm generate`
