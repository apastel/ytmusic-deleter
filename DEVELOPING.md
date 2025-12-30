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

## Github Actions
TBD

### Run Qt Designer
* Activate .venv
* `pyside6-designer`
* After updating .ui resource file...
  * `pdm generate`
