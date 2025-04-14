import logging
from json import JSONDecodeError
from pathlib import Path

import click
import ytmusicapi
from ytmusicapi.exceptions import YTMusicUserError

from . import common as const


def ensure_auth(
    credential_dir: str, oauth: bool, client_id: str = "", client_secret: str = ""
) -> ytmusicapi.YTMusic | None:
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
        yt_auth = authenticate(oauth, auth_file_path)
    except (JSONDecodeError, YTMusicUserError, FileNotFoundError):
        logging.info(f"Creating file: {auth_file_name}")
        setup_auth(oauth, client_id, client_secret, auth_file_path)
        # Authenticate after creating auth file
        yt_auth = authenticate(oauth, auth_file_path)
    finally:
        if not yt_auth:
            raise RuntimeError("Authentication failed")
        logging.info(f'Authenticated with: {auth_file_path}"')
        if oauth:
            logging.info(f"Signed in using OAuth as {yt_auth.get_account_info().get('accountName')!r}")
    return yt_auth


def setup_auth(oauth: bool, client_id: str, client_secret: str, auth_file_path: str) -> None:
    if oauth:
        if not (client_id and client_secret):
            raise click.MissingParameter(
                "Must be provided when setting up oauth.",
                param_hint="client_id and/or client_secret",
                param_type="options",
            )
        ytmusicapi.setup_oauth(
            client_id=client_id,
            client_secret=client_secret,
            filepath=auth_file_path,
            open_browser=True,
        )
    else:
        ytmusicapi.setup(filepath=auth_file_path)


def authenticate(oauth: bool, auth_file_path: str) -> ytmusicapi.YTMusic:
    if oauth:
        yt_auth = ytmusicapi.YTMusic(
            auth_file_path,
            # oauth_credentials are required by ytmusicapi but not necessary when oauth.json already exists
            oauth_credentials=ytmusicapi.OAuthCredentials(
                client_id="",
                client_secret="",
            ),
        )
    else:
        yt_auth = ytmusicapi.YTMusic(auth_file_path)
    return yt_auth
