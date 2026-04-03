import logging
import re

from retry import retry
from ytmusicapi import YTMusic
from ytmusicapi.models.content.enums import LikeStatus

BROWSER_FILENAME = "browser.json"
OAUTH_FILENAME = "oauth.json"
UNKNOWN_ARTIST = "Unknown Artist"
UNKNOWN_ALBUM = "Unknown Album"
EPISODES_FOR_LATER = "Episodes for Later"
SAVED_EPISODES_PLAYLIST_ID = "SE"
ARTIST_NAME_SCORE_CUTOFF = 90
PARENTHETICALS_REGEX = r"\s*\([^)]*\)$|\s*\[[^)]*\]$|[^\w\s]"
EXTRA_WHITESPACE_REGEX = r"\s+"
SORTABLE_ATTRIBUTES = ["artist", "album_title", "track_title", "duration"]


def unlike_song(yt_auth, track) -> bool:

    @retry(AssertionError, tries=500, delay=0.1)
    def _unlike_song(song):
        try:
            response = yt_auth.rate_song(song, LikeStatus.INDIFFERENT)
        except Exception as e:
            logging.exception(e)
        assert string_exists_in_dict(response, "Removed from liked music")
        assert string_exists_in_dict(response, "consistencyTokenJar")

    try:
        _unlike_song(track["videoId"])
        logging.info("\tRemoved track from Likes.")
        return True
    except AssertionError:
        logging.error("\tRan out of retries to remove track from Likes. Try running 'Unlike All' again.")
        return False


def strip_parentheticals(input_str: str) -> str:
    output_str = re.sub(PARENTHETICALS_REGEX, "", input_str).strip()
    output_str = re.sub(EXTRA_WHITESPACE_REGEX, " ", output_str)
    return output_str


def can_edit_playlist(playlist: dict) -> bool:
    """
    Returns True if the user owns the playlist and therefore has permission to edit it.

    In case Google changes this, we don't want this to break and prevent users from
    at least attempting to remove duplicates, so this shall return True by default if
    the ownership can't be determined
    """
    return playlist.get("owned", True) or playlist.get("id") == "LM"


def string_exists_in_dict(data: dict, search_string: str) -> bool:
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
        if search_string.lower() in str(key).lower():
            return True
        if isinstance(value, dict):
            if string_exists_in_dict(value, search_string):
                return True
        elif search_string.lower() in str(value).lower():
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
        try:
            import click

            yt_auth: YTMusic = click.get_current_context().obj["YT_AUTH"]
        except Exception as err:
            raise ValueError("yt_auth must be provided when not running in Click context") from err
    library_album = yt_auth.get_album(browse_id)
    audio_playlist_id = library_album.get("audioPlaylistId")
    if not audio_playlist_id:
        logging.error(f"Could not get audio playlist ID for album {browse_id}")
    return audio_playlist_id


def chunked(iterable, size):
    """
    Yield successive chunks of a specified size from an iterable.

    Args:
        iterable (iterable): The iterable to chunk.
        size (int): The size of each chunk.

    Returns:
        generator: A generator that yields chunks of the specified size.
    """
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


class HeaderCleanup:
    @staticmethod
    def cleanup_headers(header_lines) -> str:
        """
        Takes a string of header lines (alternating header and value) and joins them as 'header: value'.
        This is necessary when the headers were copied from Chrome/Edge, which do not format them correctly.
        If the headers are already formatted, it returns them unchanged.
        """
        logging.debug("Raw headers:\n%s", header_lines)
        if HeaderCleanup.is_already_formatted(header_lines):
            logging.debug("Headers are already formatted, returning as is.")
            return header_lines.strip()

        header_lines = HeaderCleanup.remove_client_variations_block(header_lines)
        logging.debug("Headers after removing ClientVariations block:\n%s", header_lines)

        header_lines = header_lines.strip()
        lines = [line.strip() for line in header_lines.splitlines()]

        result = []
        current_header = None
        current_value = []

        for line in lines:
            if current_header is None:
                current_header = line
            elif not current_value:
                # The very first line after the header is unconditionally part of the value
                current_value.append(line)
            else:
                # Chrome copies header names as strictly lowercase alphanumeric/hyphens.
                # If a line has uppercase, semicolons, etc., it's a wrapped fragment of the previous value!
                is_header_format = bool(line and re.match(r"^[A-Za-z0-9\-]+$", line) and len(line) < 50)

                if is_header_format:
                    result.append(f"{current_header}: {''.join(current_value)}")
                    current_header = line
                    current_value = []
                else:
                    current_value.append(line)

        # Append the final item
        if current_header is not None:
            result.append(f"{current_header}: {''.join(current_value)}")

        joined_result = "\n".join(result)
        logging.debug("Formatted headers:\n%s", joined_result)
        return joined_result

    @staticmethod
    def remove_client_variations_block(text: str) -> str:
        """
        Removes the block starting with 'Decoded:' followed by 'message ClientVariations {'
        and ending with the next '}'. Only removes the block itself, preserving any lines
        after it.
        """
        lines = text.splitlines()
        output = []
        skip = False
        brace_depth = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            # Start skipping if we see 'Decoded:' followed by 'message ClientVariations {'
            if not skip and line.strip() == "Decoded:":
                # Look ahead for 'message ClientVariations {'
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("message ClientVariations {"):
                    skip = True
                    brace_depth = lines[j].count("{") - lines[j].count("}")
                    i = j + 1
                    while i < len(lines) and brace_depth > 0:
                        brace_depth += lines[i].count("{") - lines[i].count("}")
                        i += 1
                    # Skip the closing '}' line if present
                    if i < len(lines) and lines[i].strip() == "}":
                        i += 1
                    skip = False
                    continue
            output.append(line)
            i += 1
        return "\n".join(output)

    @staticmethod
    def is_already_formatted(header_text: str) -> bool:
        """
        Returns True if the text is already formatted as 'Header: Value'.
        """
        lines = [line.strip() for line in header_text.splitlines() if line.strip()]
        if not lines:
            return False

        # Check up to the first 4 non-empty lines
        lines_to_check = lines[:4]
        colon_count = sum(1 for line in lines_to_check if ":" in line)

        # Firefox (formatted) has a colon on every line.
        # Chrome (alternating) has colons on half or fewer lines.
        return colon_count > (len(lines_to_check) / 2)
