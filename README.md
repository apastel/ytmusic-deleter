# ytmustic-deleter
The YouTube Music interface does not yet have an option to delete your music library, whether it's your uploaded songs or songs that you've added to your library from within YouTube Music.

Enter `ytmusic-deleter`: A command-line interface for performing batch delete operations on your YouTube Music library. You can use this to remove items from both your library and from your uploads.

## Setup
Until I can package this as an .exe file for people of all skill levels, you will have to run this manually on a command prompt using Python.

1. Install [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. Clone this repository to your computer and open a command prompt window inside the project's folder.
1. Run `pip install .` (the dot is important). Use a virtual environment if you're familiar with the process. If not, it's fine.
1. Obtain your YTMusic cookie and paste it into `ytmusic_deleter/headers_auth.json` in the spot indicated. To obtain your cookie use the instructions from the [ytmusicapi docs](https://ytmusicapi.readthedocs.io/en/latest/setup.html) under "Copy authentication headers". Your cookie should be a very long line of text that starts with "VISITOR_INFO". Don't share your cookie with me or anyone else.

# Usage
After running the above setup steps, Type `ytmusic-deleter` to see the usage information. There are currently two commands available:

`delete-uploads`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all tracks that you have uploaded to your YT Music library.  

>Use the `--add-to-library` or `-a` option to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads. Note that each track that gets added to your library this way will have a thumbs up "Like" in your library due to how the [ytmusicapi](https://github.com/sigma67/ytmusicapi/) works.

`remove-library`:&nbsp;&nbsp;&nbsp;&nbsp;Remove all tracks that you have added to your library from within YouTube Music.

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
Remove everything (uploads and library tracks):
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
Make sure you are running the command from inside the project folder that you downloaded from GitHub. Also make sure that you ran `pip install .` to install ytmusic-deleter. If you're still getting this error, try closing and re-opening your command prompt.

---
```
Cookie invalid. Did you paste your cookie into headers_auth.json?
```
If you see this message, be sure to follow the steps in the Setup section of this README to paste your cookie into headers_auth.json.

---
```
Failed loading provided credentials. Make sure to provide a string or a file path. Reason: Expecting value: line 1 column 1 (char 0)
Headers not found. Most likely the headers_auth.json file could not be located.
```
As the error message says, the headers_auth.json file containing your cookie could not be found. Make sure you are running the `ytmusic-deleter` command from the `ytmusic-deleter` folder, and not from the source code folder `ytmusic_deleter`.
