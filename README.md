# ytmusic-deleter-packager
A project that aims to package ytmusic-deleter into an easy to install &amp; run application

### Generate `ui_form.py`:
pyside6-uic -o src/main/python/generated/ui_main_window.py src/main/resources/main_window.ui
pyside6-uic -o src/main/python/generated/ui_auth_dialog.py src/main/resources/auth_dialog.ui
pyside6-uic -o src/main/python/generated/ui_progress_dialog.py src/main/resources/progress_dialog.ui

### Build
```
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
* Proper logging and exception handling
  * Example: Raising exception in confirmation dialog neither logs the exception or gives any indication in the UI what happened
  * Can't get this to work when the exception is raised in a slot
