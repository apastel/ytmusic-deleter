If this project helped you and you want to thank me, you can get me a beer! (I will actually use the money to buy beer, and I'll send you a virtual cheers).

<a href="https://www.buymeacoffee.com/jewbix.cube"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a beer&emoji=🍻&slug=jewbix.cube&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff"></a>

# ytmusic-deleter
A command-line interface for performing batch delete operations on your YouTube Music library. It's faster than browser-based / Javscript-based tools because it uses the YouTube Music API instead of performing the deletion in your browser. You can use this to do any of the following:
- Delete uploads
- Delete library songs
- Delete playlists
- Reset "Likes"

New in version 1.3.0, you can also sort your playlists. See the Usage information for `sort-playlist`.

## Setup
New in 1.4.0, Windows users can download a self-contained .exe file of ytmusic-deleter without having to install Python or set up a virtual environment.  

### Windows Easy "Install" Using .exe File
1. Download the latest `ytmusic-deleter-<version>.exe` from the Releases area on this GitHub repository.
1. Double-clicking the .exe file is not how to run the program. You must run it in a command window.
    - Open a Terminal/CMD window in the same folder in which the .exe was downloaded.
        - An easy way to do this is to open the folder in Windows Explorer, then Shift+Right-click on an empty space in the Explorer window and select "Open in Terminal" or "Open PowerShell window here".
1. Run ytmusic-deleter by typing the name of the .exe file and pressing Enter. You can avoid typing the full filename by just typing the first few letters and hitting the Tab key to auto-complete.

Continue to Setup Below

### Manual install using Python / PIP
1. Install [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. Open a command prompt and type `pip install ytmusic-deleter`. Use a [virtual environment](https://virtualenv.pypa.io/en/latest/) if you're familiar with the process.
1. Run ytmusic-deleter by simply entering `ytmusic-deleter` at the command line.

### Installation & Setup
1. The first time you run ytmusic-deleter, you will be asked to paste your request headers from Firefox. This allows ytmusic-deleter to make requests against your music library. To copy your request headers follow the instructions from the [ytmusicapi docs](https://ytmusicapi.readthedocs.io/en/latest/setup.html) under "Copy authentication headers".
1. Press `Enter` after pasting the headers, then press Ctrl-D to continue (Ctrl-Z then Enter again on Windows). The next time you run ytmusic-deleter, it will reuse your headers from the `headers_auth.json` file that it generated.

# Usage
When you run `ytmusic-deleter` with no parameters, you will see see the usage information. There are several commands available.

`delete-uploads`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all tracks that you have uploaded to your YT Music library.

>Use the `--add-to-library` or `-a` option to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads. Note that each track that gets added to your library this way will have a thumbs up "Like" in your library due to how the [ytmusicapi](https://github.com/sigma67/ytmusicapi/) works.

`remove-library`:&nbsp;&nbsp;&nbsp;&nbsp;Remove all tracks that you have added to your library from within YouTube Music.

`unlike-all`:&nbsp;&nbsp;&nbsp;&nbsp;Reset all Thumbs Up ratings back to neutral.

`delete-playlists`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all manually created YT Music playlists.

`delete-all`:&nbsp;&nbsp;&nbsp;&nbsp;Combo command that will run `delete-uploads`, `remove-library`, `unlike-all`, and `delete-playlists`.
### Non-deletion commands:
`sort-playlist`:&nbsp;&nbsp;&nbsp;&nbsp;Sort a playlist alphabetically by artist and then by song title.

>Use the `--shuffle` or `-s` option to shuffle the playlist instead of sorting it.
## Examples

Getting help:
```
ytmusic-deleter --help
```
This will print the usage information for `ytmusic-deleter` and exit.  
You can use the `--help` argument to print usage information for subcommands as well, as follows:
```
ytmusic-deleter delete-uploads --help
```
---
Delete all your uploads:
```
ytmusic-deleter delete-uploads
```
Delete all your uploads but add them to your YouTube Music library first:
```
ytmusic-deleter delete-uploads -a
```
Remove all your library tracks (not uploads):
```
ytmusic-deleter remove-library
```
Reset all Thumbs Up ratings back to neutral:
```
ytmusic-deleter unlike-all
```
Delete all your personally created playlists:
```
ytmusic-deleter delete-playlists
```
Remove everything (uploads, library tracks, playlists, and unlike all songs):
```
ytmusic-deleter delete-all
```
Sort a playlist called **Workout Jams**:
```
ytmusic-deleter sort-playlist "workout jams"
```

## Extra options
These supplemental options are unlikely to be helpful for most use cases and are mainly to support an app I'm working on that will use this tool.
```
Options:
  --version                  Show the version and exit.
  -l, --log-dir TEXT         Custom directory in which to write log files,
                             instead of current working directory.
  -c, --credential-dir TEXT  Custom directory in which to locate/create JSON
                             credential file, instead of current working
                             directory
  -p, --static-progress      Log the progress statically instead of an
                             animated progress bar
```
# Troubleshooting
```
ytmusic-deleter: command not found
```
or
```
'ytmusic-deleter' is not recognized as an internal or external command,
operable program or batch file.
```
Make sure you ran `pip install ytmusic-deleter` to install ytmusic-deleter. If you're still getting this error, try closing and re-opening your command prompt.

---
```
Failed loading provided credentials. Make sure to provide a string or a file path. Reason: Expecting value: line 1 column 1 (char 0)
```
You will see this printed by the [ytmusicapi](https://github.com/sigma67/ytmusicapi) the first time you run. This means that your existing request headers file (headers_auth.json) could not be found. The next few lines will prompt you to paste your request headers so this file can be generated.

---
Other various exceptions may occur while running ytmusic-deleter because there is a wide swath of possible metadata on your library, and the YouTube Music backend is changing rapidly. Most errors deleting albums have been accounted for and you may just have to delete a couple albums manually that got left behind. If there are any errors that halt the entire program in the middle of deletion, please create an Issue and post the full error.

---
