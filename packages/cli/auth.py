import logging
from json import JSONDecodeError
from pathlib import Path

import constants as const
import ytmusicapi
from ytmusicapi import YTMusic


def ensure_auth(credential_dir) -> YTMusic:
    """
    Checks for an existing oauth.json file to authenticate with.
    If one does not exist, prompt the user on the console to authenticate to
    generate one.

    See https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html
    """
    oauth_file_path: str = str(Path(credential_dir) / const.OAUTH_FILENAME)
    yt_auth = None
    try:
        logging.info(f"Attempting authentication with: {oauth_file_path}")
        yt_auth = YTMusic(oauth_file_path)
        logging.info(f'Authenticated with: {oauth_file_path}"')
    except JSONDecodeError:
        logging.info(f"Creating file: {const.OAUTH_FILENAME}")
        ytmusicapi.setup_oauth(filepath=oauth_file_path, open_browser=True)
        yt_auth = YTMusic(oauth_file_path)
        logging.info(f'Created: {oauth_file_path}"')
    finally:
        if yt_auth:
            logging.info(
                f"Logged in as {yt_auth.get_account_info().get('accountName')!r}"
            )
    return yt_auth
