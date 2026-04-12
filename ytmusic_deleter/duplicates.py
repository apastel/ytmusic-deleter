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


def _first_thumbnail_url(track: dict) -> str | None:
    thumbnails = track.get("thumbnails") or []
    if thumbnails:
        return thumbnails[0].get("url")
    return None


def _normalize_title(title: str | None) -> str:
    return strip_parentheticals((title or "")).lower()


def _resolve_yt_auth(yt_auth: YTMusic | None) -> YTMusic:
    if yt_auth:
        return yt_auth
    try:
        return get_current_context().obj["YT_AUTH"]
    except Exception as err:
        raise ValueError("yt_auth must be provided when not running in Click context") from err


def _artist_from_track(track: dict, fuzzy: bool):
    title = track.get("title")
    if not fuzzy and track.get("videoType") == VideoType.UGC and title:
        parts = title.split("-")
        if len(parts) > 1:
            return parts[0].strip()

    if track.get("artists"):
        return track.get("artists")[0].get("name")
    if track.get("artist"):
        return track.get("artist").get("name")
    return UNKNOWN_ARTIST


def _title_from_track(track: dict, fuzzy: bool):
    title = track.get("title")
    if fuzzy:
        return title

    if track.get("videoType") == VideoType.UGC and title:
        parts = title.split("-")
        if len(parts) > 1:
            return parts[1].strip()
    return title


def _compact_track(track: dict, fuzzy: bool) -> dict:
    return {
        "artist": _artist_from_track(track, fuzzy),
        "title": _title_from_track(track, fuzzy),
        "album": track.get("album").get("name") if track.get("album") else UNKNOWN_ALBUM,
        "duration": track.get("duration"),
        "thumbnail": _first_thumbnail_url(track),
        "videoId": track.get("videoId"),
        "setVideoId": track.get("setVideoId"),
        "videoType": track.get("videoType"),
    }


def _compact_tracks(tracks: list[dict], fuzzy: bool) -> list[dict]:
    return [_compact_track(track, fuzzy) for track in tracks]


def check_for_duplicates(playlist: dict, yt_auth: YTMusic = None, fuzzy: bool = False, score_cutoff: int = 80):
    yt_auth = _resolve_yt_auth(yt_auth)
    logging.info(f"Checking for duplicates in playlist {playlist.get('title')!r}")
    tracks = _compact_tracks(playlist.get("tracks"), fuzzy)
    duplicate_groups = _group_duplicate_tracks(tracks, fuzzy, score_cutoff)

    return duplicate_groups


def _group_duplicate_tracks_exact(tracks: list[dict]) -> list[list[dict]]:
    groups: list[list[dict]] = []
    group_by_video_id: dict[str, int] = {}
    group_by_artist_title: dict[tuple[str, str], int] = {}

    for track in tracks:
        video_id = track.get("videoId")
        artist = track.get("artist") or UNKNOWN_ARTIST
        title_key = _normalize_title(track.get("title"))
        artist_title_key = (artist, title_key)

        group_idx = None
        if video_id:
            group_idx = group_by_video_id.get(video_id)
        if group_idx is None:
            group_idx = group_by_artist_title.get(artist_title_key)

        if group_idx is None:
            group_idx = len(groups)
            groups.append([track])
            group_by_artist_title[artist_title_key] = group_idx
            if video_id:
                group_by_video_id[video_id] = group_idx
            continue

        groups[group_idx].append(track)
        if video_id:
            group_by_video_id[video_id] = group_idx

    return [group for group in groups if len(group) > 1]


def _group_duplicate_tracks_fuzzy(tracks: list[dict], score_cutoff: int) -> list[list[dict]]:
    groups = defaultdict(list)
    for track in tracks:
        video_id = track.get("videoId")
        # Check for existing group with same videoId or similar title and artist
        matched_key = None
        for key, group in groups.items():
            if (video_id and any(t["videoId"] == video_id for t in group)) or _get_matching_algorithm(
                track, group, True, score_cutoff
            ):
                matched_key = key
                break

        if matched_key is not None:
            groups[matched_key].append(track)
        else:
            # No matching group found, create a new group
            # Use id(track) as key to avoid None videoId collisions
            group_key = video_id if video_id else id(track)
            groups[group_key].append(track)

    return [group for group in groups.values() if len(group) > 1]


def _group_duplicate_tracks(tracks: list[dict], fuzzy: bool, score_cutoff: int) -> list[list[dict]]:
    """
    Groups tracks in a list considering both videoId and similar title with same artist.

    Args:
      tracks: A list of dictionaries, each containing "artist", "title", and "videoId" keys.

    Returns:
      A list of lists, where each inner list contains duplicate tracks.
    """
    if not fuzzy:
        return _group_duplicate_tracks_exact(tracks)

    return _group_duplicate_tracks_fuzzy(tracks, score_cutoff)


def _get_matching_algorithm(track, group, fuzzy: bool, score_cutoff: int):
    if fuzzy:
        return (_artists_match(track, group[0], score_cutoff)) and all(
            _partial_match(_normalize_title(t["title"]), _normalize_title(track["title"]), score_cutoff)
            for t in group
        )

    similar_title_key = (track["artist"], _normalize_title(track["title"]))
    return group[0]["artist"] == similar_title_key[0] and all(
        _normalize_title(t["title"]) == similar_title_key[1] for t in group
    )


def determine_tracks_to_remove(duplicate_groups: list[list[dict]]) -> tuple[list[dict], list[list[dict]] | None]:
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
                    f"\tWill delete {track.get('artist')} - {track.get('title')!r} as it is an exact duplicate."
                )
        if len(unique_group) > 1:
            unique_groups.append(unique_group)
    return unique_groups, tracks_to_remove


def _partial_match(title_a, title_b, score_cutoff):
    score = fuzz.partial_ratio(title_a, title_b)

    # Make sure this result at least passes the score cutoff
    is_match = score >= score_cutoff
    if is_match:
        logging.debug(
            f"""
            Token A: {title_a}
            Token B: {title_b}
            Score: {score} ✅
        """
        )
        return is_match
    return False


def _artists_match(track_a, track_b, score_cutoff):
    if any(t.get("videoType") == VideoType.UGC for t in [track_a, track_b]):
        return True
    return bool(_partial_match(track_a["artist"], track_b["artist"], score_cutoff))
