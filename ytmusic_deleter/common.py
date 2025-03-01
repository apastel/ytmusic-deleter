import re
from ytmusicapi import YTMusic
import logging
import click

LIKE = "LIKE"
INDIFFERENT = "INDIFFERENT"
BROWSER_FILENAME = "browser.json"
OAUTH_FILENAME = "oauth.json"
UNKNOWN_ARTIST = "Unknown Artist"
UNKNOWN_ALBUM = "Unknown Album"
ARTIST_NAME_SCORE_CUTOFF = 90
PARENTHETICALS_REGEX = r"\s*\([^)]*\)$|\s*\[[^)]*\]$|[^\w\s]"
EXTRA_WHITESPACE_REGEX = r"\s+"
SORTABLE_ATTRIBUTES = ["artist", "album_title", "track_title", "duration"]


def strip_parentheticals(input_str: str) -> str:
    output_str = re.sub(PARENTHETICALS_REGEX, "", input_str).strip()
    output_str = re.sub(EXTRA_WHITESPACE_REGEX, " ", output_str)
    return output_str.lower()


def can_edit_playlist(playlist: dict) -> bool:
    """
    Returns True if the user owns the playlist and therefore has permission to edit it.

    In case Google changes this, we don't want this to break and prevent users from
    at least attempting to remove duplicates, so this shall return True by default if
    the ownership can't be determined
    """
    return playlist.get("owned", True) or playlist.get("id") == "LM"


def search_string_in_dict(data: dict, search_string: str) -> bool:
    """
    Recursively searches for a string in the keys or values of a dictionary,
    including nested dictionaries.

    Args:
        data (dict): The dictionary to search within.
        search_string (str): The string to search for.

    Returns:
        bool: True if the string is found, False otherwise.
    """
    for key, value in data.items():
        if search_string in str(key):
            return True
        if isinstance(value, dict):
            if search_string_in_dict(value, search_string):
                return True
        elif search_string in str(value):
            return True
    return False


def get_album_audio_playlist_id(browse_id: str, yt_auth: YTMusic = None) -> str | None:
    """
    Get the audio playlist ID for an album.

    Args:
        browse_id (str): The browse ID of the album.

    Returns:
        str: The audio playlist ID or None if it could not be found.
    """
    # Allow passing in yt_auth from pytest
    if not yt_auth:
        yt_auth: YTMusic = click.get_current_context().obj["YT_AUTH"]
    library_album = yt_auth.get_album(browse_id)
    audio_playlist_id = library_album.get("audioPlaylistId")
    if not audio_playlist_id:
        # Monkey patch until https://github.com/sigma67/ytmusicapi/issues/743 is fixed.
        import ytmusicapi.mixins.browsing

        ytmusicapi.mixins.browsing.parse_album_header_2024 = parse_album_header_2025

        library_album = yt_auth.get_album(browse_id)
        audio_playlist_id = library_album["audioPlaylistId"]
        if not audio_playlist_id:
            logging.error(f"Could not get audio playlist ID for album {browse_id}")
    return audio_playlist_id
    

from ytmusicapi.parsers._utils import *


# flake8: noqa
def parse_album_header_2025(response):
    from ytmusicapi.helpers import to_int
    from ytmusicapi.parsers.songs import parse_song_runs, parse_like_status
    from ytmusicapi.parsers.podcasts import parse_base_header

    header = nav(response, [*TWO_COLUMN_RENDERER, *TAB_CONTENT, *SECTION_LIST_ITEM, *RESPONSIVE_HEADER])
    album = {
        "title": nav(header, TITLE_TEXT),
        "type": nav(header, SUBTITLE),
        "thumbnails": nav(header, THUMBNAILS),
        "isExplicit": nav(header, SUBTITLE_BADGE_LABEL, True) is not None,
    }
    album["description"] = nav(header, ["description", *DESCRIPTION_SHELF, *DESCRIPTION], True)
    album_info = parse_song_runs(header["subtitle"]["runs"][2:])
    album_info["artists"] = [parse_base_header(header)["author"]]
    album.update(album_info)
    if len(header["secondSubtitle"]["runs"]) > 1:
        album["trackCount"] = to_int(header["secondSubtitle"]["runs"][0]["text"])
        album["duration"] = header["secondSubtitle"]["runs"][2]["text"]
    else:
        album["duration"] = header["secondSubtitle"]["runs"][0]["text"]
    # add to library/uploaded
    buttons = header["buttons"]
    album["audioPlaylistId"] = nav(
        find_object_by_key(buttons, "musicPlayButtonRenderer"),
        ["musicPlayButtonRenderer", "playNavigationEndpoint", *WATCH_PID],
        True,
    )
    service = nav(
        find_object_by_key(buttons, "toggleButtonRenderer"),
        ["toggleButtonRenderer", "defaultServiceEndpoint"],
        True,
    )
    album["likeStatus"] = "INDIFFERENT"
    if service:
        album["likeStatus"] = parse_like_status(service)
    return album
