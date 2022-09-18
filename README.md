# ytmusic-deleter-packager
A project that aims to package ytmusic-deleter into an easy to install and run application

### Generate forms from UI files:
pyside6-uic -o src/main/python/generated/ui_main_window.py src/main/resources/main_window.ui
pyside6-uic -o src/main/python/generated/ui_auth_dialog.py src/main/resources/auth_dialog.ui
pyside6-uic -o src/main/python/generated/ui_progress_dialog.py src/main/resources/progress_dialog.ui
pyside6-uic -o src/main/python/generated/ui_sort_playlists_dialog.py src/main/resources/sort_playlists_dialog.ui

### Build
```
(from venv)
pip install -r requirements/dev.txt
pre-commit install
fbs clean
fbs freeze
fbs installer
```

# ToDo
~~* Print stdout to in-app textarea instead of separate terminal window~~
~~* Don't require running as administrator~~
~~* Initial screen for inputting request headers (instead of separate terminal window)~~
~~* Copy ytmusicapi/locales from site-packages instead of including in the project tree~~
  ~~* Or use cli.exe~~
* Exceptions aren't displayed to the user when they happen in a Slot
~~* Exceptions aren't sent to Sentry when they happen on the main thread (https://github.com/mherrmann/fbs/issues/283)~~
