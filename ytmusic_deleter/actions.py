import logging
import re
import time
from random import shuffle as unsort

from ytmusic_deleter import common
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusic_deleter.duplicates import determine_tracks_to_remove
from ytmusic_deleter.progress import manager
from ytmusic_deleter.progress import update_progress
from ytmusic_deleter.uploads import maybe_delete_uploaded_albums
from ytmusicapi.models.content.enums import LikeStatus
from ytmusicapi.type_alias import JsonDict

CANCELLED_MESSAGE = "Operation cancelled by user."


def _is_history_empty_error(err: Exception) -> bool:
    return str(err) == "None"


def _get_history_items(yt_auth):
    try:
        return yt_auth.get_history()
    except Exception as err:
        if _is_history_empty_error(err):
            return None
        raise


def _create_history_progress_bar(total: int, static_progress: bool):
    return manager.counter(
        total=total,
        desc="History Items Deleted",
        unit="items",
        enabled=not static_progress,
    )


def _delete_history_item(yt_auth, item) -> bool:
    artist = item["artists"][0]["name"] if item.get("artists") else common.UNKNOWN_ARTIST
    logging.info(f"\tProcessing history item: {artist} - {item['title']!r}")
    response = yt_auth.remove_history_items(item["feedbackToken"])
    processed = response.get("feedbackResponses")[0].get("isProcessed")
    if processed:
        logging.info(f"\tDeleted history item: {artist} - {item['title']!r}")
        return True
    logging.info(f"\tFailed to delete history item: {response}")
    return False


def _process_history_batch(ctx: "ActionContext", history_items) -> int:
    yt_auth = ctx.yt_auth
    progress_bar = _create_history_progress_bar(len(history_items), ctx.static_progress)
    logging.info(f"Found {len(history_items)} history items to delete.")
    deleted_this_round = 0
    for item in history_items:
        if ctx.is_cancelled():
            logging.info(CANCELLED_MESSAGE)
            return deleted_this_round
        if _delete_history_item(yt_auth, item):
            deleted_this_round += 1
        update_progress(progress_bar)
    return deleted_this_round


def _playlist_artist(track):
    return track["artists"][0]["name"] if track.get("artists") else common.UNKNOWN_ARTIST


def _validate_sort_attributes(custom_sort):
    invalid_keys = [attr for attr in custom_sort if attr not in common.SORTABLE_ATTRIBUTES]
    if invalid_keys:
        raise ValueError(f"Invalid sort option(s): {', '.join(invalid_keys)}")


def _get_selected_playlists(all_playlists, playlist_titles):
    lowercase_playlist_titles = [title.lower() for title in playlist_titles]
    selected_playlist_list = [
        playlist for playlist in all_playlists if playlist["title"].lower() in lowercase_playlist_titles
    ]
    return lowercase_playlist_titles, selected_playlist_list


def _build_desired_tracklist(playlist_tracks, shuffle, custom_sort, reverse, playlist_title):
    if shuffle:
        logging.info(f"\tPlaylist: {playlist_title} will be shuffled")
        desired_tracklist = list(playlist_tracks)
        unsort(desired_tracklist)
        return desired_tracklist
    return sorted(playlist_tracks, key=lambda t: make_sort_key(t, custom_sort), reverse=reverse)


def _log_missing_set_video_ids(cur_track, track_after):
    logging.error("Encountered track(s) with missing 'setVideoId'. Cannot sort the following track(s):")
    if "setVideoId" not in cur_track:
        logging.error(f"setVideoId attribute not in cur_track: {cur_track}")
    if "setVideoId" not in track_after:
        logging.error(f"setVideoId attribute not in track_after: {track_after}")


def _move_playlist_track(yt_auth, playlist_id, cur_track, track_after, cur_artist, track_after_artist):
    if "setVideoId" not in cur_track or "setVideoId" not in track_after:
        _log_missing_set_video_ids(cur_track, track_after)
        return False

    response = yt_auth.edit_playlist(
        playlist_id,
        moveItem=(
            cur_track["setVideoId"],
            track_after["setVideoId"],
        ),
    )
    if not response:
        logging.error(
            f"Failed to move {cur_artist} - {cur_track['title']!r} "
            f"before {track_after_artist} - {track_after['title']!r}"
        )
    return True


def _update_current_tracklist(current_tracklist, cur_track, cur_idx):
    moving_set_video_id = cur_track.get("setVideoId")
    current_idx = next(
        (i for i, track in enumerate(current_tracklist) if track.get("setVideoId") == moving_set_video_id),
        None,
    )
    if current_idx is None:
        try:
            current_idx = current_tracklist.index(cur_track)
        except ValueError:
            current_idx = None

    if current_idx is not None:
        moved_track = current_tracklist.pop(current_idx)
        current_tracklist.insert(cur_idx, moved_track)


def _sort_single_playlist(ctx: "ActionContext", selected_playlist, shuffle, custom_sort, reverse):
    yt_auth = ctx.yt_auth
    logging.info(f"Processing playlist: {selected_playlist['title']}")
    playlist = yt_auth.get_playlist(selected_playlist["playlistId"], limit=None)
    if not common.can_edit_playlist(playlist):
        logging.error(f"Cannot modify playlist {playlist.get('title')!r}. You are not the owner of this playlist.")
        return

    current_tracklist = list(playlist["tracks"])
    desired_tracklist = _build_desired_tracklist(
        playlist["tracks"], shuffle, custom_sort, reverse, selected_playlist["title"]
    )

    progress_bar = manager.counter(
        total=len(desired_tracklist),
        desc=f"{selected_playlist['title']!r} Tracks {'Shuffled' if shuffle else 'Sorted'}",
        unit="tracks",
        enabled=not ctx.static_progress,
    )

    for cur_idx, cur_track in enumerate(desired_tracklist):
        track_after = current_tracklist[cur_idx]
        cur_artist = _playlist_artist(cur_track)
        track_after_artist = _playlist_artist(track_after)
        if cur_track != track_after:
            logging.debug(
                f"Moving {cur_artist} - {cur_track['title']!r} before {track_after_artist} - {track_after['title']!r}"
            )
            try:
                moved = _move_playlist_track(
                    yt_auth,
                    playlist["id"],
                    cur_track,
                    track_after,
                    cur_artist,
                    track_after_artist,
                )
                if moved:
                    _update_current_tracklist(current_tracklist, cur_track, cur_idx)
            except Exception:
                logging.error(
                    f"Failed to move {cur_artist} - {cur_track['title']!r} "
                    f"before {track_after_artist} - {track_after['title']!r}"
                )
                _update_current_tracklist(current_tracklist, cur_track, cur_idx)
        update_progress(progress_bar)


def _get_not_found_playlists(lowercase_playlist_titles, selected_playlist_list):
    selected_titles = [x["title"].lower() for x in selected_playlist_list]
    return [title for title in lowercase_playlist_titles if title not in selected_titles]


class ActionContext:
    __slots__ = ("yt_auth", "static_progress", "cancelled")

    def __init__(self, yt_auth, static_progress=False, cancelled=None):
        self.yt_auth = yt_auth
        self.static_progress = static_progress
        self.cancelled = cancelled or (lambda: False)

    def is_cancelled(self):
        return self.cancelled()


def delete_uploads(ctx: ActionContext, add_to_library=False, score_cutoff=90):
    (albums_deleted, albums_total) = maybe_delete_uploaded_albums(
        yt_auth=ctx.yt_auth,
        add_to_library=add_to_library,
        score_cutoff=score_cutoff,
        static_progress=ctx.static_progress,
        cancelled=ctx.is_cancelled,
    )
    logging.info(f"Deleted {albums_deleted} out of {albums_total} uploaded albums (or songs).")
    remaining_count = albums_total - albums_deleted
    if add_to_library and remaining_count > 0:
        logging.info(f"\tRemaining {remaining_count} albums (or songs) could not be added to your library.")
        logging.info("\tRe-run without the 'Add to library' option to delete the rest.")
    return albums_deleted, albums_total


def remove_library(ctx: ActionContext):
    yt_auth = ctx.yt_auth
    logging.info("Retrieving all library albums...")
    try:
        library_albums = yt_auth.get_library_albums(limit=None)
        logging.info(f"Retrieved {len(library_albums)} albums from your library.")
    except Exception:
        logging.exception("Failed to get library albums.")
        library_albums = []

    global progress_bar
    progress_bar = manager.counter(
        total=len(library_albums),
        desc="Albums Processed",
        unit="albums",
        enabled=not ctx.static_progress,
    )
    albums_removed = remove_library_items(ctx, library_albums)

    logging.info("Retrieving all songs...")
    try:
        library_songs = yt_auth.get_library_songs(limit=None)
        logging.info(f"Retrieved {len(library_songs)} songs from your library.")
    except Exception:
        logging.exception("Failed to get library songs.")
        library_songs = []

    progress_bar = manager.counter(
        total=len(library_songs),
        desc="Songs Processed",
        unit="songs",
        enabled=not ctx.static_progress,
    )
    songs_removed = remove_library_items(ctx, library_songs)

    podcasts_removed, library_podcasts = remove_library_podcasts(ctx)

    remove_episodes_for_later(ctx)

    items_removed = albums_removed + songs_removed + podcasts_removed
    items_total = len(library_albums) + len(library_songs) + len(library_podcasts)
    logging.info(f"Removed {items_removed} out of {items_total} albums, songs, and podcasts from your library.")
    return items_removed, items_total


def remove_library_podcasts(ctx: ActionContext):
    yt_auth = ctx.yt_auth
    logging.info("Retrieving all podcasts...")
    library_podcasts = yt_auth.get_library_podcasts(limit=None)
    library_podcasts = list(filter(lambda podcast: podcast["channel"]["id"], library_podcasts))
    logging.info(f"Retrieved {len(library_podcasts)} podcasts from your library.")

    progress_bar = manager.counter(
        total=len(library_podcasts),
        desc="Podcasts Removed",
        unit="podcasts",
        enabled=not ctx.static_progress,
    )

    podcasts_removed = 0
    for podcast in library_podcasts:
        podcast_id = podcast.get("podcastId")
        title = podcast.get("title")
        if not podcast_id:
            logging.debug(f"\tCan't delete podcast {title!r} because it doesn't have an ID.")
            continue
        response = yt_auth.rate_playlist(podcast_id, LikeStatus.INDIFFERENT)
        if "actions" in response:
            logging.info(f"\tRemoved {title!r} from your library.")
            podcasts_removed += 1
        else:
            logging.error(f"\tFailed to remove {title!r} from your library.")
        update_progress(progress_bar)

    logging.info(f"Removed {podcasts_removed} out of {len(library_podcasts)} podcasts from your library.")
    return podcasts_removed, library_podcasts


def remove_library_items(ctx: ActionContext, library_items):
    yt_auth = ctx.yt_auth
    items_removed = 0
    for item in library_items:
        if ctx.is_cancelled():
            logging.info(CANCELLED_MESSAGE)
            break
        logging.debug(f"Full album or song item: {item}")
        artist = item["artists"][0]["name"] if item.get("artists") else common.UNKNOWN_ARTIST
        title = item.get("title")
        logging.info(f"Processing item: {artist} - {title!r}")

        playlist_id = item.get("playlistId")
        response = None
        feedback_tokens = item.get("feedbackTokens")
        if playlist_id:
            logging.debug(f"Removing album using id: {playlist_id}")
            response = yt_auth.rate_playlist(playlist_id, LikeStatus.INDIFFERENT)
        elif feedback_tokens and isinstance(feedback_tokens, dict) and feedback_tokens.get("remove"):
            logging.debug("This is a song, removing using feedback token.")
            remove_token = feedback_tokens.get("remove")
            assert remove_token is not None
            response = yt_auth.edit_song_library_status([remove_token])
        else:
            logging.error(
                f"""
                Library item {artist} - {title!r} was in an unexpected format, unable to remove.
                Provide this to the developer:
                {item}
            """
            )

        if response and "Removed from library" in str(response):
            logging.debug(response)
            logging.info(f"\tRemoved {artist} - {title!r} from your library.")
            items_removed += 1
        else:
            logging.error(f"\tFailed to remove {artist} - {title!r} from your library.")
        update_progress(progress_bar)
    return items_removed


def remove_episodes_for_later(ctx: ActionContext):
    yt_auth = ctx.yt_auth
    logging.info(f"Retrieving the {common.EPISODES_FOR_LATER!r} playlist...")
    episodes_for_later_playlist = yt_auth.get_playlist(common.SAVED_EPISODES_PLAYLIST_ID, limit=None)

    if not episodes_for_later_playlist:
        logging.warning(f"{common.EPISODES_FOR_LATER!r} playlist was not found, skip removing episodes.")
        return

    playlist_episodes = episodes_for_later_playlist.get("tracks", [])
    if not playlist_episodes:
        logging.info(f"{common.EPISODES_FOR_LATER!r} playlist already empty.")
        return

    playlist_id = episodes_for_later_playlist.get("id", "")
    if not playlist_id:
        logging.error(f"{common.EPISODES_FOR_LATER!r} playlist missing 'id' attribute, skip removing episodes")
        return

    logging.info(f"Clearing {len(playlist_episodes)} episodes from the {common.EPISODES_FOR_LATER!r} playlist...")
    response = yt_auth.remove_playlist_items(playlist_id, playlist_episodes)
    status = response if isinstance(response, str) else response.get("status", "")
    if status == "STATUS_SUCCEEDED":
        logging.info(f"Successfully cleared the {common.EPISODES_FOR_LATER!r} playlist.")
    else:
        logging.error(
            f"May have failed to delete the episodes in the {common.EPISODES_FOR_LATER!r} playlist. Status: {status}"
        )


def unlike_all(ctx: ActionContext):
    yt_auth = ctx.yt_auth
    logging.info("Retrieving all your liked songs...")
    try:
        your_likes = yt_auth.get_liked_songs(limit=None)
    except Exception:
        logging.error("\tNo liked songs found or error retrieving liked songs.")
        raise
    logging.info(f"\tRetrieved {len(your_likes['tracks'])} liked songs.")
    logging.info("Begin unliking songs...")

    progress_bar = manager.counter(
        total=len(your_likes["tracks"]),
        desc="Songs Unliked",
        unit="songs",
        enabled=not ctx.static_progress,
    )

    songs_unliked = 0
    for track in your_likes["tracks"]:
        if ctx.is_cancelled():
            logging.info(CANCELLED_MESSAGE)
            break
        artist = track["artists"][0]["name"] if track.get("artists") else common.UNKNOWN_ARTIST
        title = track["title"]
        logging.info(f"Processing track: {artist} - {title!r}")
        success = common.unlike_song(yt_auth, track)
        if success:
            songs_unliked += 1
        else:
            logging.error(f"\tFailed to unlike {artist} - {title!r}")
        update_progress(progress_bar)

    logging.info(f"Finished unliking {songs_unliked} out of {len(your_likes['tracks'])} songs.")
    return songs_unliked, len(your_likes["tracks"])


def delete_playlists(ctx: ActionContext):
    yt_auth = ctx.yt_auth
    logging.info("Retrieving all your playlists...")
    library_playlists = yt_auth.get_library_playlists(limit=None)
    library_playlists = list(filter(lambda playlist: playlist["playlistId"] != "LM", library_playlists))
    logging.info(f"\tRetrieved {len(library_playlists)} playlists.")
    logging.info("Begin deleting playlists...")

    progress_bar = manager.counter(
        total=len(library_playlists),
        desc="Playlists Deleted",
        unit="playlists",
        enabled=not ctx.static_progress,
    )

    playlists_deleted = 0
    for playlist in library_playlists:
        if ctx.is_cancelled():
            logging.info(CANCELLED_MESSAGE)
            break
        logging.info(f"Processing playlist: {playlist['title']}")
        try:
            response = yt_auth.delete_playlist(playlist["playlistId"])
            if response:
                logging.info(f"\tRemoved playlist {playlist['title']!r} from your library.")
                playlists_deleted += 1
            else:
                logging.error(f"\tFailed to remove playlist {playlist['title']!r} from your library.")
        except Exception:
            logging.error(
                f"\tCould not delete playlist {playlist['title']!r}. You might not have permission to delete it."
            )
        update_progress(progress_bar)

    logging.info(f"Deleted {playlists_deleted} out of {len(library_playlists)} playlists from your library.")
    remove_episodes_for_later(ctx)
    return playlists_deleted, len(library_playlists)


def delete_history(ctx: ActionContext, items_deleted=0):
    yt_auth = ctx.yt_auth
    logging.info("Begin deleting history...")
    while True:
        try:
            history_items = _get_history_items(yt_auth)
        except Exception as e:
            logging.exception(e)
            logging.info(f"Deleted {items_deleted} history items.")
            return items_deleted

        if not history_items:
            logging.info("History is empty, nothing left to delete.")
            logging.info(f"Deleted {items_deleted} history items.")
            return items_deleted

        deleted_this_round = _process_history_batch(ctx, history_items)
        items_deleted += deleted_this_round
        if ctx.is_cancelled():
            return items_deleted

        if deleted_this_round == 0:
            logging.warning("No additional history items were deleted in the last pass. Stopping retries.")
            logging.info(f"Deleted {items_deleted} history items.")
            return items_deleted

        logging.info("Refreshing history list to continue deletion...")
        time.sleep(1)


def delete_all(ctx: ActionContext):
    delete_uploads(ctx)
    remove_library(ctx)
    delete_playlists(ctx)
    unlike_all(ctx)
    delete_history(ctx)


def sort_playlist(ctx: ActionContext, shuffle, playlist_titles, custom_sort, reverse):
    yt_auth = ctx.yt_auth
    _validate_sort_attributes(custom_sort)

    all_playlists = yt_auth.get_library_playlists(limit=None)
    lowercase_playlist_titles, selected_playlist_list = _get_selected_playlists(all_playlists, playlist_titles)

    for selected_playlist in selected_playlist_list:
        if ctx.is_cancelled():
            logging.info(CANCELLED_MESSAGE)
            break
        _sort_single_playlist(ctx, selected_playlist, shuffle, custom_sort, reverse)

    not_found_playlists = _get_not_found_playlists(lowercase_playlist_titles, selected_playlist_list)
    if not_found_playlists:
        raise ValueError(
            f"No playlists found named {', '.join(not_found_playlists)!r}. Double-check your playlist name(s) "
            '(or surround them "with quotes") and try again.'
        )


def remove_duplicates(ctx: ActionContext, playlist_title, _exact, fuzzy, score_cutoff):
    yt_auth = ctx.yt_auth
    playlist = get_library_playlist_from_title(yt_auth, playlist_title)

    duplicates = check_for_duplicates(playlist, yt_auth, fuzzy, score_cutoff)
    if not duplicates:
        logging.info("No duplicates found. If you think this is an error open an issue on GitHub or message on Discord")
        return

    items_to_remove, _ = determine_tracks_to_remove(duplicates)
    if not items_to_remove:
        logging.info("Finished: No duplicate tracks were marked for deletion.")
        return
    logging.info(f"Removing {len(items_to_remove)} tracks total.")
    playlist_id = playlist.get("id")
    if not isinstance(playlist_id, str) or not playlist_id:
        logging.error("Playlist ID is missing or invalid. Cannot remove duplicates.")
        return
    if playlist_id == "LM":
        for song in items_to_remove:
            success = common.unlike_song(yt_auth, song)
            logging.info(song)
            if not success:
                logging.error(f"\tFailed to unlike {song['artist']} - {song['title']!r}")
    else:
        for chunk in common.chunked(items_to_remove, 50):
            yt_auth.remove_playlist_items(playlist_id, chunk)
    logging.info("Finished removing duplicate tracks.")


def add_all_to_playlist(ctx: ActionContext, playlist_title, library, uploads):
    if not (library or uploads):
        raise ValueError("You must specify either --library or --uploads.")

    yt_auth = ctx.yt_auth
    playlist = get_library_playlist_from_title(yt_auth, playlist_title)
    if library:
        logging.info("User has selected 'Library' option. Retrieving all library songs...")
        songs_to_add = yt_auth.get_library_songs(limit=None)
        logging.info(f"Retrieved {len(songs_to_add)} library songs.")
    else:
        logging.info("User has selected 'Uploads' option. Retriving all uploaded songs...")
        songs_to_add = yt_auth.get_library_upload_songs(limit=None)
        logging.info(f"Retrieved {len(songs_to_add)} uploaded songs.")

    if not songs_to_add:
        raise ValueError("No songs were found to add to the playlist.")

    video_ids = [song["videoId"] for song in songs_to_add if "videoId" in song]
    logging.info(f"Preparing to add all {len(video_ids)} songs to playlist {playlist.get('title')!r}.")
    response = yt_auth.add_playlist_items(playlist.get("id"), video_ids, duplicates=True)
    if "status" not in response or "STATUS_SUCCEEDED" not in response.get("status", ""):
        logging.error(response)
        raise RuntimeError("API did not return a success message. See response object above.")
    logging.info(f"Finished adding {len(video_ids)} songs to playlist {playlist.get('title')!r}.")


def add_all_to_library(ctx: ActionContext, playlist_title_or_id):
    yt_auth = ctx.yt_auth
    logging.info("Loading playlist...")
    playlist = get_library_playlist_from_title(
        yt_auth, playlist_title_or_id, fail_if_not_exist=False, fail_if_not_owner=False
    )
    if not playlist:
        try:
            playlist = yt_auth.get_playlist(playlist_title_or_id, limit=None)
        except KeyError as err:
            raise ValueError(
                f"No playlist named {playlist_title_or_id!r} found in your library.\n"
                f"If {playlist_title_or_id!r} is a playlist ID, that playlist is private or does not exist."
            ) from err

    playlist_tracks = playlist.get("tracks")
    if not playlist_tracks:
        raise ValueError("Could not find any tracks in the selected playlist")

    playlist_title = playlist.get("title")
    logging.info(
        f"Will attempt to add all {len(playlist_tracks)} tracks from playlist {playlist_title!r} to your library"
    )

    progress_bar = manager.counter(
        total=len(playlist_tracks),
        desc="Playlist Tracks Processed",
        unit="tracks",
        enabled=not ctx.static_progress,
    )

    added_tracks_count = 0
    for track in playlist_tracks:
        if ctx.is_cancelled():
            logging.info("Operation cancelled by user.")
            break
        track_str = f"{track['artists'][0]['name']} - {track['title']!r}"
        logging.info(f"Processing item: {track_str}")
        add_token = track.get("feedbackTokens", {}).get("add")
        if add_token:
            response = yt_auth.edit_song_library_status([add_token])
            if "actions" in response:
                added_tracks_count += 1
                logging.info(f"Added {track_str} to your library")
            else:
                logging.error(f"Failed to add {track_str} to your library")
        else:
            logging.error(f"{track_str} is a video and cannot be added to your library")
        update_progress(progress_bar)

    logging.info(
        f"Finished adding {added_tracks_count} out of {len(playlist_tracks)} tracks from "
        f"playlist {playlist_title!r} to your library"
    )


def get_library_playlist_from_title(
    yt_auth, playlist_title: str, fail_if_not_exist: bool = True, fail_if_not_owner: bool = True
) -> JsonDict | None:
    all_playlists = yt_auth.get_library_playlists(limit=None)
    selected_playlist_id = next(
        (
            playlist["playlistId"]
            for playlist in all_playlists
            if playlist.get("title").lower() == playlist_title.lower()
        ),
        None,
    )
    if not selected_playlist_id:
        if fail_if_not_exist:
            raise ValueError(
                f"No playlist found named {playlist_title!r}. Double-check your playlist name "
                '(or surround it "with quotes") and try again.'
            )
        return None

    playlist = yt_auth.get_playlist(selected_playlist_id, limit=None)
    playlist_title_formatted = playlist.get("title")
    logging.info(f"Retrieved playlist named {playlist_title_formatted!r} with {len(playlist.get('tracks'))} tracks.")
    if fail_if_not_owner and not common.can_edit_playlist(playlist):
        raise ValueError(
            f"Cannot modify playlist {playlist_title_formatted!r}. You are not the owner of this playlist."
        )
    return playlist


def make_sort_key(track, sort_attributes):
    artists = track["artists"]
    artist = artists[0]["name"].lower() if artists else "z"
    artist = re.sub(r"^(the |a )", "", artist)
    album = track["album"]
    album_title = album["name"].lower() if album else "z"
    album_title = re.sub(r"^(the |a )", "", album_title)
    track_title = track["title"].lower()
    duration = track.get("duration_seconds", 0)  # noqa: F841

    if sort_attributes:
        sort_values = {
            "artist": artist,
            "album_title": album_title,
            "track_title": track_title,
            "duration": duration,
        }
        return tuple(sort_values[attr] for attr in sort_attributes)
    else:
        return artist, album_title, track_title
