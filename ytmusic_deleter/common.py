import logging
import re

import click
from ytmusicapi import YTMusic

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
        if search_string in str(key):
            return True
        if isinstance(value, dict):
            if string_exists_in_dict(value, search_string):
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
        lines = header_lines.splitlines()

        # Remove empty lines
        lines = [line.strip() for line in lines if line.strip()]

        result = []
        i = 0
        while i < len(lines) - 1:
            header = lines[i]
            value = lines[i + 1]
            result.append(f"{header}: {value}")
            i += 2
        # Handle odd number of lines
        if i < len(lines):
            result.append(lines[i])
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
        Returns True if either of the first two non-empty lines contains a colon followed by at least one
        non-space character, indicating it's already formatted as 'Header: Value'.
        """
        checked = 0
        for line in header_text.splitlines():
            line = line.strip()
            if not line:
                continue
            checked += 1
            if ":" in line:
                parts = line.split(":", 1)
                if parts[1].strip():
                    return True
            if checked >= 2:
                break
        return False
