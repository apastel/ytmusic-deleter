# ytmusic-deleter: Delete your YouTube Music library
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/apastel/ytmusic-deleter/total?label=.exe%20Downloads)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ytmusic-deleter?logo=pypi&logoColor=yellow&label=PyPI%20Downloads)](https://pypi.org/project/ytmusic-deleter/)
![GitHub Release](https://img.shields.io/github/v/release/apastel/ytmusic-deleter)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-exe.yml)
[![Release test](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/build-deb.yml)
[![Pytest](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml/badge.svg)](https://github.com/apastel/ytmusic-deleter/actions/workflows/pytest.yml)
![Codecov](https://img.shields.io/codecov/c/github/apastel/ytmusic-deleter?color=green)
![Discord](https://img.shields.io/discord/1156973782741827686?logo=discord)

YTMusic Deleter is an installable program for performing batch delete operations on your YouTube Music library, since
currently there is no built-in option to do this. This tool is faster than browser-based / Javscript-based tools because
it uses the YouTube Music API to make rapid requests against your library instead of doing the deletion manually in your browser.

If this project helped you and you want to thank me, you can <a href="https://www.buymeacoffee.com/jewbix.cube">get me a beer!</a>

<a href="https://www.buymeacoffee.com/jewbix.cube"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a beer&emoji=🍻&slug=jewbix.cube&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff"></a>

![Get help on Discord!](https://invidget.switchblade.xyz/M9t5H8njrM)


Features
--------
* Remove all songs and podcasts from your Library
* Delete all of your Uploads
  * Option to automatically add the corresponding album to your library from within YT Music
* Delete all of your playlists
* Reset all of your "Liked" ratings
* Delete your play history
* Sort your playlists

![YTMusic Deleter screenshot](https://i.imgur.com/ZmGl58E.gif)  

## Installation
### Easy Install (Windows or Debian Linux Only)
Windows or Debian Linux users (including Ubuntu) can download an .exe (or .deb, for Linux) to install the YTMusic Deleter GUI (Graphical User Interface).

Find the .exe (or .deb) file in the [Releases](https://github.com/apastel/ytmusic-deleter/releases) area. Just click the latest release and look at the Assets section.  
> Please note you may get a browser warning when downloading the file, and a Windows warning for installing files from an unknown publisher. Click the "More Info" button, then the "Run Anyway" button to finish installing. This warning appears whenever you install something from an unsigned publisher.

### (Advanced) Command-line interface for non-Windows users
See [CLI README](ytmusic_deleter/README.md) 

## Setup
Once installed and running, simply click the "Log In" button to authenticate to your YouTube Music account.
You will see your Google account name and profile photo to ensure you are logged into the correct account.

This login process uses the [Google API flow for TV devices](https://developers.google.com/youtube/v3/guides/auth/devices)
and is handled by the [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html), which handles all of the
API interaction in this app.

[Video Tutorial](https://youtu.be/f4RTUZ6kLUI?si=Rh_qzc21LS3xuw-e&t=60) on using YT Music Deleter
> This video shows an older version of the UI. The authentication process has been simplified. New video coming soon!


## Troubleshooting
Various exceptions may occur while running ytmusic-deleter because there is a wide swath of possible metadata on your library, and the YouTube Music backend is changing rapidly. Most errors deleting albums have been accounted for and you may just have to delete a couple albums manually that got left behind. If there are any errors that halt the entire program in the middle of deletion, please create an Issue and post the full error.
