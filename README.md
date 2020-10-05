# ytmusic-deleter
A command-line interface for performing batch delete operations on your YouTube Music library. You can use this to remove items from both your library and from your uploads.

## Setup
1. Install [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. Open a command prompt and type `pip install ytmusic-deleter`. Use a [virtual environment](https://virtualenv.pypa.io/en/latest/) if you're familiar with the process.
1. Run ytmusic-deleter by simply entering `ytmusic-deleter` at the command line.
1. The first time you run ytmusic-deleter, you will be asked to paste your request headers from Firefox. This allows ytmusic-deleter to make requests against your music library. To copy your request headers follow the instructions from the [ytmusicapi docs](https://ytmusicapi.readthedocs.io/en/latest/setup.html) under "Copy authentication headers".
1. Press `Enter` after pasting the headers, then press Ctrl-D to continue (Ctrl-Z then Enter again on Windows). The next time you run ytmusic-deleter, it will reuse your headers from the `headers_auth.json` file that it generated.

# Usage
Type `ytmusic-deleter` to see the usage information. There are currently four commands available:

`delete-uploads`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all tracks that you have uploaded to your YT Music library.  

>Use the `--add-to-library` or `-a` option to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads. Note that each track that gets added to your library this way will have a thumbs up "Like" in your library due to how the [ytmusicapi](https://github.com/sigma67/ytmusicapi/) works.

`remove-library`:&nbsp;&nbsp;&nbsp;&nbsp;Remove all tracks that you have added to your library from within YouTube Music.  

`unlike-all`:&nbsp;&nbsp;&nbsp;&nbsp;Reset all Thumbs Up ratings back to neutral.  

`delete-all`:&nbsp;&nbsp;&nbsp;&nbsp;Combo command that will run `delete-uploads`, `remove-library`, and `unlike-all`.
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
Remove everything (uploads, library tracks, and unlike all songs):
```
ytmusic-deleter delete-all
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
