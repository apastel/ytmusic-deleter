# Developer's Guide
## Dev Container
This project uses Dev Containers to set up the development environment. Open the project in VS Code and use the Dev Containers
extension to build the dev container. Upon completion, the YTMusic Deleter application should automatically start up in a
X11 GUI window.

## Setup
* Install [Python](https://www.python.org/)
* Install [pdm](https://pdm-project.org/en/latest/#installation)
* `pdm install -dG lint,test` to skip installing deps for GUI, one of which is fbs_pro which is a paid library
  * Install fbs_pro with curl -L https://drive.google.com/uc?id={FBS_URL_ID} --output fbs_pro-1.2.1.tar.gz
  * `pdm install`
* Activate .venv
* `pre-commit install`

## Run
* `ytmusic-deleter` to run CLI
* `pdm fbs run` to run GUI

## Unit Tests
* `cp tests/resources/test.example.cfg tests/resources/test.cfg`
* `wget --content-disposition -P tests/resources/ "https://drive.google.com/uc?export=download&id=18AP7mQqQxqj2_delNyhoCNa6UCUCN9-P"`
* `ytmusicapi browser` to create browser.json for uploads, put in tests/resources
* `ytmusicapi oauth` to create oauth.json for other tests, put in tests/resources
* `pdm run pytest`

## Releases
* `pdm version [major|minor|patch]` to bump version

### Publish CLI
* `pdm publish`

### Create GUI .exe
```
pdm freeze-prep
pdm fbs freeze
pdm fbs installer
```

### Run Qt Designer
* Activate .venv
* `pyside6-designer`
* After updating .ui resource file...
  * `pdm generate`
