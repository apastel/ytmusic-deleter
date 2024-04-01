# ytmusic-deleter: Delete your YouTube Music library
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/apastel/ytmusic-deleter/total?label=.exe%20Downloads)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ytmusic-deleter?label=PyPI%20Downloads)
![GitHub Release](https://img.shields.io/github/v/release/apastel/ytmusic-deleter)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/apastel/ytmusic-deleter/pytest.yml?branch=main&label=tests)
![Codecov](https://img.shields.io/codecov/c/github/apastel/ytmusic-deleter?color=green)
![Discord](https://img.shields.io/discord/1156973782741827686?logo=discord)

This is the command-line interface for ytmusic-deleter. For the graphical Windows .exe edition, visit the [main page](https://github.com/apastel/ytmusic-deleter)

## Command-line interface install using Python / PIP
The CLI version of ytmusic-deleter is for advanced users who would rather use a command-line or aren't running Windows.
> For the graphical Windows .exe edition, visit the [main page](https://github.com/apastel/ytmusic-deleter)

Installtion instructions of this command-line interface:
1. Install [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. Open a command prompt and type `pip install ytmusic-deleter`. Use a [virtual environment](https://virtualenv.pypa.io/en/latest/) if you're familiar with the process.
1. Run ytmusic-deleter by simply entering `ytmusic-deleter` at the command line.

### Usage
When you run `ytmusic-deleter` with no parameters, you will see see the usage information. There are several commands available.

`delete-uploads`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all tracks that you have uploaded to your YT Music library.

>Use the `--add-to-library` or `-a` option to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads.
When using the `-a` option, you can also enable fuzzy matching with `--fuzzy` or `-f`. This is a less strict matching algorithm that will find more matches,
but may find inaccurrate matches in its current experimental state. Use the `--score-cutoff` or `-s` option to raise or lower the default matching score cutoff of 90. A value closer to 100 will be more strict, and a value closer to 0 will be less strict.

`remove-library`:&nbsp;&nbsp;&nbsp;&nbsp;Remove all tracks that you have added to your library from within YouTube Music.

`unlike-all`:&nbsp;&nbsp;&nbsp;&nbsp;Reset all Thumbs Up ratings back to neutral.

`delete-playlists`:&nbsp;&nbsp;&nbsp;&nbsp;Delete all manually created YT Music playlists.

`delete-all`:&nbsp;&nbsp;&nbsp;&nbsp;Combo command that will run `delete-uploads`, `remove-library`, `unlike-all`, and `delete-playlists`.
#### Non-deletion commands:
`sort-playlist`:&nbsp;&nbsp;&nbsp;&nbsp;Sort a playlist alphabetically by artist and then by song title.

>Use the `--shuffle` or `-s` option to shuffle the playlist instead of sorting it.
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
Sort a playlist called **Workout Jams**:
```
ytmusic-deleter sort-playlist "workout jams"
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
