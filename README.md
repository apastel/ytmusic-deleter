# ytmustic-deleter
Delete your entire uploaded YouTube Music library in one fell swoop. This will delete all your uploaded albums and songs. It will not remove songs that you added to your library from within YouTube Music's online catalog.

## EXE File
My intent with this is to package it into a neat little .exe you can run, but so far I'm running into issues with both PyInstaller and cx_Freeze.

# How To Use
In the meantime since I haven't been able to package this as an executable file yet, you will have to run this manually with Python.

That means having [Python](https://www.python.org/downloads/) installed on your computer, and using Pip to install the [YouTube Music API](https://github.com/sigma67/ytmusicapi)

Brief, brief instructions until I flesh this out:  
1. Install latest [Python](https://www.python.org/downloads/). Make sure it is available on your PATH.
1. From a command line, run `pip install ytmusicapi`. Use a virtual environment if you're familiar with the process. If not, it's fine.
1. Clone this repository to your computer and open a command prompt window inside the `ytmusic-deleter` folder.
1. Obtain your YTMusic cookie and paste it into `headers_auth.json` in the spot indicated. To obtain your cookie use the instructions from the [ytmusicapi docs](https://ytmusicapi.readthedocs.io/en/latest/setup.html) under "Copy authentication headers". Your cookie should be a very long line of text that starts with "VISITOR_INFO". Don't share your cookie with me or anyone else.
1. From the ytmusic-deleter directory you cloned, run `python main.py`
