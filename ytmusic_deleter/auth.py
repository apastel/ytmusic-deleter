import logging
from json import JSONDecodeError
from pathlib import Path

import ytmusicapi
from ytmusicapi import YTMusic

from . import common as const


def ensure_auth(credential_dir, oauth) -> YTMusic:
    """
    Checks for an existing browser.json / oauth.json file to authenticate with.
    If one does not exist, prompt the user on the console to authenticate to
    generate one.

    See https://ytmusicapi.readthedocs.io/en/stable/setup/index.html
    """
    auth_file_name = const.OAUTH_FILENAME if oauth else const.BROWSER_FILENAME
    auth_file_path: str = str(Path(credential_dir) / auth_file_name)
    yt_auth = None
    try:
        logging.info(f"Attempting authentication with: {auth_file_path}")
        yt_auth = YTMusic(auth_file_path)
        logging.info(f'Authenticated with: {auth_file_path}"')
    except JSONDecodeError:
        logging.info(f"Creating file: {auth_file_name}")
        if oauth:
            ytmusicapi.setup_oauth(filepath=auth_file_path, open_browser=True)
        else:
            ytmusicapi.setup(filepath=auth_file_path)
        yt_auth = YTMusic(auth_file_path)
        logging.info(f'Created: {auth_file_path}"')
    finally:
        if yt_auth and oauth:
            logging.info(f"Signed in as {yt_auth.get_account_info().get('accountName')!r}")
    return yt_auth
