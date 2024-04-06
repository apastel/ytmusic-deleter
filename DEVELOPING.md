# Developer's Guide
## Operating System
Windows and Linux are both supported for developing, testing, releasing, and installing YTMusic Deleter.
Mac may be supported but never been thoroughly tested.
Things to note:
* Git Bash is recommmended for Windows development
* Linux debian package may not produce a desktop icon (have to run /opt/YTMusic_Deleter/YTMusic_Deleter after installing .deb package)

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
* `curl -o tests/resources/test.mp3 https://www.kozco.com/tech/piano2-CoolEdit.mp3`
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
