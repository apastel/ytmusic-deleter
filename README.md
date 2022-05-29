# ytmusic-deleter-packager
A project that aims to package ytmusic-deleter into an easy to install &amp; run application

### Generate `ui_form.py`:
`$ pyuic5 -o src/main/python/ui_form.py src/main/resources/main_window.ui`
`$ pyuic5 -o src/main/python/auth_dialog.py src/main/resources/auth_dialog.ui`

# ToDo
~~* Print stdout to in-app textarea instead of separate terminal window~~
~~* Don't require running as administrator~~
~~* Initial screen for inputting request headers (instead of separate terminal window)~~
* Copy ytmusicapi/locales from site-packages instead of including in the project tree
  * Or use cli.exe