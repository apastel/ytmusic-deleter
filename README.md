# ytmusic-deleter: Delete your YouTube Music library
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/apastel/ytmusic-deleter/total?label=.exe%20Downloads)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ytmusic-deleter?logo=pypi&logoColor=yellow&label=PyPI%20Downloads)](https://pypi.org/project/ytmusic-deleter/)
![GitHub Release](https://img.shields.io/github/v/release/apastel/ytmusic-deleter)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml)
[![Pytest](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml)
![Codecov](https://img.shields.io/codecov/c/github/apastel/ytmusic-deleter?color=green)
[![Discord](https://img.shields.io/discord/1156973782741827686?logo=discord)](https://discord.gg/M9t5H8njrM)

YTMusic Deleter is an installable program for performing batch delete operations on your YouTube Music library, since
currently there is no built-in option to do this. This tool is faster than browser-based / Javscript-based tools because
it uses the YouTube Music API to make rapid requests against your library instead of doing the deletion manually in your browser.
It also has additional features for playlist management, like sorting and removing duplicates.

If this project helped you and you want to thank me, you can <a href="https://www.buymeacoffee.com/jewbix.cube">get me a beer!</a>

<a href="https://www.buymeacoffee.com/jewbix.cube"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a beer&emoji=🍻&slug=jewbix.cube&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff"></a>

[![Get help on Discord!](https://invidget.switchblade.xyz/M9t5H8njrM)](https://discord.gg/M9t5H8njrM)


Features
--------
### Deleting
* Remove all songs and podcasts from your Library
* Delete all of your Uploads
  * Option to automatically add the corresponding album to your library from within YT Music
* Delete all of your playlists
* Reset all of your "Liked" ratings
* Delete your play history
### Playlist Utilities
* Sort your playlists using any combination of: Artist, Album, Track Title, and Duration
* Remove duplicates from your playlists
* Add all of your uploads or library songs to a particular playlist

![YTMusic Deleter screenshot](https://i.imgur.com/TVpB6xY.gif)  

## Installation
### Easy Install (Windows or Debian Linux Only)
Windows or Debian Linux users (including Ubuntu) can download an .exe (or .deb, for Linux) to install the YTMusic Deleter GUI (Graphical User Interface).

Find the .exe (or .deb) file in the [Releases](https://github.com/apastel/ytmusic-deleter/releases) area. Just click the latest release and look at the Assets section.  
> Please note you may get a browser warning when downloading the file, and a Windows warning for installing files from an unknown publisher. Click the "More Info" button, then the "Run Anyway" button to finish installing. This warning appears whenever you install something from an unsigned publisher.

### (Advanced) Command-line interface for non-Windows users
See [CLI README](ytmusic_deleter/README.md) 

## Setup
Once installed and running, click the "Sign In" button to authenticate to your YouTube Music account.

Since Google has removed the ability to sign in using OAuth, you must now sign in using a cookie from your browser.

Follow the instructions in the [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#copy-authentication-headers)
project to copy your request headers to your clipboard. Then paste them into the window in YTMusic Deleter.
> Note: It's recommended to use Firefox for copying the headers since Firefox conveniently has a "Copy Request Headers" button.

[Video Tutorial](https://youtu.be/oV-yLi1AW1c) on using YTMusic Deleter


## Troubleshooting
Various exceptions may occur while running ytmusic-deleter because there is a wide swath of possible metadata on your library, and the YouTube Music backend is changing rapidly. Most errors deleting albums have been accounted for and you may just have to delete a couple albums manually that got left behind. If there are any errors that halt the entire program in the middle of deletion, please create an Issue and post the full error.
