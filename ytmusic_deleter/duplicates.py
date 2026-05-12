import logging
from collections import defaultdict

from click import get_current_context
from InquirerPy import get_style
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from thefuzz import fuzz
from ytmusic_deleter.common import strip_parentheticals
from ytmusic_deleter.common import UNKNOWN_ALBUM
from ytmusic_deleter.common import UNKNOWN_ARTIST
from ytmusicapi import YTMusic
from ytmusicapi.models.content.enums import VideoType


def check_for_duplicates(playlists: list[dict], yt_auth: YTMusic = None, fuzzy: bool = False, score_cutoff: int = 80):
    # Allow passing in yt_auth from pytest
    if not yt_auth:
        try:
            from click import get_current_context
            yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
        except Exception as err:
            raise ValueError("yt_auth must be provided when not running in Click context") from err

    all_tracks = []
    for playlist in playlists:
        logging.info(f"Checking for duplicates in playlist {playlist.get('title')!r}")
        for track in playlist.get("tracks", []):
            track["_playlist_id"] = playlist.get("id")
            track["_playlist_title"] = playlist.get("title")
            all_tracks.append(track)

    def get_artist_name(track):
        # If this is user-generated content on YouTube, then the actual artist name is usually
        # the first part of the title, like "Avenged Sevenfold - Nobody"
        # Note: Fuzzy matching will do this separately
        if not fuzzy and track.get("videoType") == VideoType.UGC:
            parts = track.get("title").split("-")
            if len(parts) > 1:
                return parts[0].strip()

        artist = UNKNOWN_ARTIST
        if track.get("artists"):
            artist = track.get("artists")[0].get("name")
        elif track.get("artist"):
            artist = track.get("artist").get("name")
        return artist

    def get_title_name(track):
        if fuzzy:
            # strip parens otherwise everything with (Remix) will be considered same
            return track.get("title")

        # If this is user-generated content on YouTube, then the actual title is usually the
        # second part of the title field, like "Avenged Sevenfold - Nobody"
        if track.get("videoType") == VideoType.UGC:
            parts = track.get("title").split("-")
            if len(parts) > 1:
                return parts[1].strip()
        return track.get("title")

    # Trim the fat of the tracks object
    tracks = [
        {
            "artist": get_artist_name(track),
            "title": get_title_name(track),
            "album": track.get("album").get("name") if track.get("album") else UNKNOWN_ALBUM,
            "duration": track.get("duration"),
            "thumbnail": track.get("thumbnails")[0].get("url") if track.get("thumbnails") else None,
            "videoId": track.get("videoId"),
            "setVideoId": track.get("setVideoId"),
            "videoType": track.get("videoType"),
            "_playlist_id": track.get("_playlist_id"),
            "_playlist_title": track.get("_playlist_title"),
        }
        for track in all_tracks
    ]
    duplicate_groups = _group_duplicate_tracks(tracks, fuzzy, score_cutoff)

    return duplicate_groups


def _group_duplicate_tracks(tracks: list[dict], fuzzy: bool, score_cutoff: int) -> list[list[dict]]:
    """
    Groups tracks in a list considering both videoId and similar title with same artist.

    Args:
      tracks: A list of dictionaries, each containing "artist", "title", and "videoId" keys.

    Returns:
      A list of lists, where each inner list contains duplicate tracks.
    """
    groups = defaultdict(list)
    for track in tracks:
        # Check for existing group with same videoId or similar title and artist
        for group in groups.values():
            if any(t["videoId"] == track["videoId"] for t in group) or _get_matching_algorithm(
                track, group, fuzzy, score_cutoff
            ):
                groups[group[0]["videoId"]].append(track)
                break  # Exit loop after finding a matching group

        # No matching group found, create a new group
        else:
            groups[track["videoId"]].append(track)

    # Flatten groups with duplicates into a list of lists
    return [group for group in groups.values() if len(group) > 1]


def _get_matching_algorithm(track, group, fuzzy: bool, score_cutoff: int):
    if fuzzy:
        return (_artists_match(track, group[0], score_cutoff)) and all(
            _partial_match(strip_parentheticals(t["title"]), track["title"], score_cutoff) for t in group
        )

    similar_title_key = (track["artist"], strip_parentheticals(track["title"]).lower())
    return group[0]["artist"] == similar_title_key[0] and all(
        strip_parentheticals(t["title"]).lower() == similar_title_key[1] for t in group
    )


def determine_tracks_to_remove(duplicate_groups: list[list[dict]]) -> tuple[list[dict], list[list[dict]] | None]:
    logging.info(f"There are {len(duplicate_groups)} sets of duplicates across your playlists.")

    # Automatically mark exact dupes for deletion
    logging.info("Automatically deleting tracks that are exact duplicates of other tracks.")
    remaining_dupe_groups, tracks_to_remove = _remove_exact_dupes(duplicate_groups)

    ctx = get_current_context(silent=True)
    if not ctx or ctx.params["exact"]:
        return tracks_to_remove, remaining_dupe_groups

    # Now go through each remaining dupe group and ask which ones they want to keep
    for group in remaining_dupe_groups:
        selected_tracks = inquirer.checkbox(
            message="Select the track(s) you want to REMOVE.",
            instruction="Use the arrow keys and space bar to make your selection, then press Enter.",
            choices=[
                Choice(
                    track,
                    name=(
                        f"[{track.get('_playlist_title')}] {track.get('artist')} - "
                        f"{track.get('title')!r} - {track.get('album')}. Length: {track.get('duration')}"
                    ),
                )
                for track in group
            ],
            disabled_symbol="[ ]",
            enabled_symbol="[X]",
            style=get_style({"checkbox": "red"}, style_override=False),
            border=True,
            wrap_lines=True,
        ).execute()
        tracks_to_remove.extend(selected_tracks)

    return tracks_to_remove, None


def _remove_exact_dupes(duplicate_groups) -> tuple[list[list[dict]], list[dict]]:
    """
    Removes tracks with duplicate videoIds from each group in duplicate_groups.

    Args:
        duplicate_groups: A list of lists, where each inner list contains dicts representing tracks.

    Returns:
        A list of lists with unique videoIds in each group and an updated tracks_to_delete list.
    """
    unique_groups = []
    tracks_to_remove = []
    for group in duplicate_groups:
        seen_video_ids = set()
        unique_group = []
        for track in group:
            video_id = track.get("videoId")
            if video_id not in seen_video_ids:
                seen_video_ids.add(video_id)
                unique_group.append(track)
            else:
                tracks_to_remove.append(track)
                logging.info(
                    f"\tWill delete [{track.get('_playlist_title')}] {track.get('artist')} - "
                    f"{track.get('title')!r} as it is an exact duplicate."
                )
        if len(unique_group) > 1:
            unique_groups.append(unique_group)
    return unique_groups, tracks_to_remove


def _partial_match(titleA, titleB, score_cutoff):
    score = fuzz.partial_ratio(titleA, titleB)

    # Make sure this result at least passes the score cutoff
    is_match = score >= score_cutoff
    if is_match:
        logging.debug(
            f"""
            Token A: {titleA}
            Token B: {titleB}
            Score: {score} ✅
        """
        )
        return is_match


def _artists_match(trackA, trackB, score_cutoff):
    if any(t.get("videoType") == VideoType.UGC for t in [trackA, trackB]):
        return True
    return _partial_match(trackA["artist"], trackB["artist"], score_cutoff)
