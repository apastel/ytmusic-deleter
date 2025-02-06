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
### Easy Install on Windows, macOS, or Debian Linux
Windows, macOS, or Debian Linux users (including Ubuntu) can download an .exe, .dmg, or .deb file to install the YTMusic Deleter GUI (Graphical User Interface).

Find the executable file in the [Releases](https://github.com/apastel/ytmusic-deleter/releases) area. Just click the latest release and look at the Assets section.  
* Windows users: Download the Windows-Installer.exe
* Linux users (Debian only): Download the Linux-Installer.deb
> Please note you may get a browser warning when downloading the file, and a Windows warning for installing files from an unknown publisher. Click the "More Info" button, then the "Run Anyway" button to finish installing. This warning appears whenever you install something from an unsigned publisher.
#### macOS users: Download the MacOS-Installer.dmg
  * Choose the `x86_64` version if you have an Intel CPU (2020 and earlier Macs usually have this)
  * Choose the `arm` version if you have a newer Mac with an Apple silicon chip.
  * You will know if you chose the wrong version because you will get an error saying "You can't open the application 'YTMusic_Deleter' because this application is not supported on this Mac."
  * You must open Terminal and run this command before using YTMusic Deleter on macOS:
    ```
    xattr -d com.apple.quarantine ~/Downloads/YTMusic_Deleter-[x.y.z]-MacOS-Installer_[arch].dmg
    ```
    replacing `[x.y.z]` and `[arch]` with the actual values, and replacing `~/Downloads` with the correct folder (if your downloads go in some other folder).  
    If you do not run this command, you will see the following error when running the program: "'YTMusic_Deleter' is damaged and can't be opened. You should eject the disk image."  
    This happens because macOS automatically blocks DMG files downloaded from the internet that it doesn't recognize, and running this command will remove it from quarantine.

## Setup
Once installed and running, click the "Sign In" button to authenticate to your YouTube Music account.

Since Google has removed the ability to sign in to 3rd party apps using OAuth, you must now sign in using a cookie from your browser.

Follow the instructions in the [ytmusicapi](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#copy-authentication-headers) documentation or my [sign-in video tutorial](https://youtu.be/FZ7gaMTUYN4)
to copy your request headers to your clipboard. Then paste them into the window in YTMusic Deleter.
> It's recommended to use Firefox for copying the headers since Firefox conveniently has a "Copy Request Headers" button.

### (Advanced) Command-line interface
If you would prefer to use the command-line interface, see [CLI README](ytmusic_deleter/README.md) for instructions on running the CLI version of YTMusic Deleter. This is completely separate from the GUI version. There is no reason to download both -- use one or the other.

## Troubleshooting
[Video Tutorial](https://youtu.be/oV-yLi1AW1c) on using YTMusic Deleter in general (this shows an outdated sign-in method which was unfortunately deprecated).

[Sign-in video tutorial](https://youtu.be/FZ7gaMTUYN4)

If you see:
```
ytmusicapi.exceptions.YTMusicServerError: Server returned HTTP 401: Unauthorized.
You must be signed in to perform this operation.
```
then your sign-in has expired (happens monthly, roughly). Click the profile icon and click "Sign Out", then sign back in
again by following the steps in [Setup](./README.md#setup).

Various other exceptions may occur while running ytmusic-deleter because there is a wide swath of possible metadata on your library, and the YouTube Music backend is changing rapidly. Most errors deleting albums have been accounted for and you may just have to delete a couple albums manually that got left behind. If there are any errors that halt the entire program in the middle of deletion, please create an Issue and post the full error.
