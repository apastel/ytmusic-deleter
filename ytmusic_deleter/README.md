# ytmusic-deleter: Delete your YouTube Music library
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/apastel/ytmusic-deleter/total?label=.exe%20Downloads)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ytmusic-deleter?logo=pypi&logoColor=yellow&label=PyPI%20Downloads)](https://pypi.org/project/ytmusic-deleter/)
![GitHub Release](https://img.shields.io/github/v/release/apastel/ytmusic-deleter)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-dmg.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-dmg.yml)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml)
[![Pytest](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml)
![Codecov](https://img.shields.io/codecov/c/github/apastel/ytmusic-deleter?color=green)
[![Discord](https://img.shields.io/discord/1156973782741827686?logo=discord)](https://discord.gg/M9t5H8njrM)

This is the command-line interface for ytmusic-deleter. For the graphical user interface edition, visit the [main page](https://github.com/apastel/ytmusic-deleter)

## Command-line interface install using Python / PIP
The CLI version of ytmusic-deleter is for advanced users who would rather use a command-line.
> For the graphical user interface edition, visit the [main page](https://github.com/apastel/ytmusic-deleter)

Installation instructions of this command-line interface:
1. Install [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. Open a command prompt and type `pip install ytmusic-deleter`. Use a [virtual environment](https://virtualenv.pypa.io/en/latest/) if you're familiar with the process.
1. Run ytmusic-deleter by simply entering `ytmusic-deleter` at the command line.

## Authentication (Browser)

The first time you run ytmusic-deleter, you will be asked to paste your request headers from your browser.
This allows ytmusic-deleter to make requests against your music library. Follow the instructions in the 
[ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#copy-authentication-headers) documentation
or my [sign-in video tutorial](https://youtu.be/FZ7gaMTUYN4) to copy your request headers to your clipboard, then paste
them into the terminal window and press the shown key sequence.

```sh
$ ytmusic-deleter whoami
[2024-11-16 12:51:05] Attempting authentication with: C:\Users\<username>\AppData\Roaming\YTMusic_Deleter\browser.json
[2024-11-16 12:51:05] Creating file: browser.json
Please paste the request headers from Firefox and press 'Enter, Ctrl-Z, Enter' to continue:
```
> If you are running macOS, please see the [special pasting instructions](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#using-the-headers-in-your-project)
in the "macOS special pasting instructions" section of the ytmusicapi docs.


### Usage
When you run `ytmusic-deleter` with no parameters, you will see see the usage information. There are several commands available.

`delete-uploads`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all tracks that you have uploaded to your YT Music library.

>Use the `--add-to-library` or `-a` option to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads.
When using the `-a` option, you can also use the `--score-cutoff` or `-s` option to raise or lower the default matching score cutoff of 85. A value closer to 100 will be more strict, and a value closer to 0 will be less strict.

`remove-library`:&nbsp;&nbsp;&nbsp;&nbsp;Remove all tracks that you have added to your library from within YouTube Music.

`unlike-all`:&nbsp;&nbsp;&nbsp;&nbsp;Reset all Thumbs Up ratings back to neutral.

`delete-playlists`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all manually created YT Music playlists.

`delete-all`:&nbsp;&nbsp;&nbsp;&nbsp;Combo command that will run `delete-uploads`, `remove-library`, `unlike-all`, and `delete-playlists`.
#### Non-deletion commands:
`sort-playlist`:&nbsp;&nbsp;&nbsp;&nbsp;Sort a playlist alphabetically by artist and then by song title.

>Use the `--shuffle` or `-s` option to shuffle the playlist instead of sorting it.  
Use `--custom-sort` or `-c` to define custom sort parameters Available parameters are: `artist`, `album_title`, `track_title`, and `duration`. See below for examples.  
Use `--reverse` to reverse the sort order.

`remove-duplicates`:&nbsp;&nbsp;&nbsp;&nbsp;Remove duplicate tracks from a particular playlist.

>Use the `--exact` or `-e` option to only remove exact duplicates. This will skip the portion
that checks for duplicates that are similar matches but not the same exact track.

`add-all-to-playlist`:&nbsp;&nbsp;&nbsp;&nbsp;Add all library songs or uploads to a particular playlist.
#### Examples

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
Sort a playlist called **Workout Jams** using the default settings (sorts by artist then album title):
```
ytmusic-deleter sort-playlist "workout jams"
```

Sort a playlist using custom sorting attributes (attributes are applied in order):
```
ytmusic-deleter sort-playlist "workout jams" --custom-sort artist --custom-sort album_title --custom-sort track_title
```

Remove duplicate tracks from a playlist called "Focus"
```
ytmusic-deleter remove-duplicates focus
```

Add all uploads to a playlist called "All my uploads"
```
ytmusic-deleter add-all-to-playlist "All my uploads" --uploads
```

#### Extra options
These supplemental options are unlikely to be helpful for most use cases and are mainly to support the GUI version.
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
#### Troubleshooting
```
ytmusic-deleter: command not found
```
or
```
'ytmusic-deleter' is not recognized as an internal or external command,
operable program or batch file.
```
Make sure you ran `pip install ytmusic-deleter` to install ytmusic-deleter. If you're still getting this error, try closing and re-opening your command prompt.
