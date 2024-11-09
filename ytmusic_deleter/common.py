import re

LIKE = "LIKE"
INDIFFERENT = "INDIFFERENT"
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
