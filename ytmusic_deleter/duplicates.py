import logging
from collections import defaultdict
from typing import Dict
from typing import List

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


def check_for_duplicates(playlist: dict, yt_auth: YTMusic = None):
    # Allow passing in yt_auth from pytest
    if not yt_auth:
        yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    logging.info(f"Checking for duplicates in playlist {playlist.get('title')!r}")
    tracks = playlist.get("tracks")

    def get_artist_name(track):
        # If this is user-generated content on YouTube, then the actual artist name is usually
        # the first part of the title, like "Avenged Sevenfold - Nobody"
        # Note: Fuzzy matching will do this separately
        ctx = get_current_context(silent=True)
        if ctx and not ctx.params["fuzzy"] and track.get("videoType") == VideoType.UGC:
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
        ctx = get_current_context(silent=True)
        if ctx and ctx.params["fuzzy"]:
            # strip parens otherwise everything with (Remix) will be considered same
            return strip_parentheticals(track.get("title"))

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
            "thumbnail": track.get("thumbnails")[0].get("url"),
            "videoId": track.get("videoId"),
            "setVideoId": track.get("setVideoId"),
            "videoType": track.get("videoType"),
        }
        for track in tracks
    ]
    duplicate_groups = _group_duplicate_tracks(tracks)

    return duplicate_groups


def _group_duplicate_tracks(tracks: List[Dict]) -> List[List[Dict]]:
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
            if any(t["videoId"] == track["videoId"] for t in group) or _get_matching_algorithm(track, group):
                groups[group[0]["videoId"]].append(track)
                break  # Exit loop after finding a matching group

        # No matching group found, create a new group
        else:
            groups[track["videoId"]].append(track)

    # Flatten groups with duplicates into a list of lists
    return [group for group in groups.values() if len(group) > 1]


def _get_matching_algorithm(track, group):
    ctx = get_current_context(silent=True)
    if ctx and ctx.params["fuzzy"]:
        score_cutoff = ctx.params["score_cutoff"]
        return (_artists_match(track, group[0], score_cutoff)) and all(
            _partial_match(t["title"], track["title"], score_cutoff) for t in group
        )

    similar_title_key = (track["artist"], strip_parentheticals(track["title"]).lower())
    return group[0]["artist"] == similar_title_key[0] and all(
        strip_parentheticals(t["title"]).lower() == similar_title_key[1] for t in group
    )


def determine_tracks_to_remove(duplicate_groups: List[List[Dict]]) -> tuple[List[Dict], List[List[Dict]] | None]:
    logging.info(f"There are {len(duplicate_groups)} sets of duplicates in your playlist.")

    # Automatically mark exact dupes for deletion
    logging.info("Automatically deleting tracks that are exact duplicates of other tracks in the playlist.")
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
                    name=f"{track.get('artist')} - {track.get('title')!r} - {track.get('album')}. Length: {track.get('duration')}",
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


def _remove_exact_dupes(duplicate_groups) -> tuple[List[List[Dict]], List[Dict]]:
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
                    f"\tWill delete {track.get('artist')} - {track.get('title')!r} as it is an exact duplicate."
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
