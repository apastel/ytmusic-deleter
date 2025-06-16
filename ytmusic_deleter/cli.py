import logging.handlers
import os
import re
import sys
import time
from pathlib import Path
from random import shuffle as unsort
from time import strftime

import click
from click import get_current_context
from ytmusic_deleter import common
from ytmusic_deleter._version import __version__
from ytmusic_deleter.auth import do_auth
from ytmusic_deleter.duplicates import check_for_duplicates
from ytmusic_deleter.duplicates import determine_tracks_to_remove
from ytmusic_deleter.progress import manager
from ytmusic_deleter.uploads import maybe_delete_uploaded_albums
from ytmusicapi import YTMusic


@click.group()
@click.version_option(__version__)
@click.option(
    "--credential-dir",
    "-c",
    default=os.getcwd(),
    help="Custom directory in which to locate/create JSON credential file, instead of current working directory",
)
@click.option(
    "--static-progress",
    "-p",
    is_flag=True,
    help="Log the progress statically instead of an animated progress bar",
)
@click.option(
    "--log-dir",
    "-l",
    default=os.getcwd(),
    help="Custom directory in which to write log files, instead of current working directory.",
)
@click.option("--no-logfile", "-n", is_flag=True, help="Only log to stdout, no file logging")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose (debug) logging")
@click.option("--oauth", "-o", is_flag=True, help="Enable OAuth authentication")
@click.option("--client-id", "-y", help="Client ID (for OAuth)")
@click.option("--client-secret", "-z", help="Client secret (for OAuth)")
@click.pass_context
def cli(
    ctx: click.Context, log_dir, credential_dir, static_progress, no_logfile, verbose, oauth, client_id, client_secret
):
    """Perform batch delete operations on your YouTube Music library."""

    handlers = [logging.StreamHandler(sys.stdout)]
    if not no_logfile:
        handlers.append(logging.FileHandler(Path(log_dir) / f"ytmusic-deleter-cli_{strftime('%Y-%m-%d')}.log"))
    logging.basicConfig(
        force=True,
        level=logging.DEBUG if verbose else logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        encoding="utf-8",
    )

    if ctx.obj is not None:
        # Allows yt_auth to be provided by pytest
        yt_auth: YTMusic = ctx.obj
    else:
        yt_auth: YTMusic = do_auth(credential_dir, oauth, client_id, client_secret)
    ctx.ensure_object(dict)
    ctx.obj["STATIC_PROGRESS"] = static_progress
    ctx.obj["YT_AUTH"] = yt_auth


@cli.command()
def whoami():
    """Print the name of the authenticated user, or sign in"""
    pass


@cli.command()
@click.option(
    "--add-to-library",
    "-a",
    is_flag=True,
    help="Add the corresponding album to your library before deleting a song from uploads.",
)
@click.option(
    "--score-cutoff",
    "-s",
    default=90,
    help="When combined with the --add-to-library flag, this optional integer argument between 0 and 100 is used when finding matches in the YTM online catalog. No matches with a score less than this number will be added to your library. Defaults to 85.",  # noqa: B950
)
@click.pass_context
def delete_uploads(ctx: click.Context, **kwargs):
    """Delete all songs that you have uploaded to your YT Music library."""
    (albums_deleted, albums_total) = maybe_delete_uploaded_albums()
    logging.info(f"Deleted {albums_deleted} out of {albums_total} uploaded albums (or songs).")
    remaining_count = albums_total - albums_deleted
    if (ctx.params["add_to_library"]) and remaining_count > 0:
        logging.info(f"\tRemaining {remaining_count} albums (or songs) could not be added to your library.")
        logging.info("\tRe-run without the 'Add to library' option to delete the rest.")
    return (albums_deleted, albums_total)


@cli.command()
@click.pass_context
def remove_library(ctx: click.Context):
    """Remove all songs and podcasts that you have added to your library from within YouTube Music."""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
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
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    albums_removed = remove_library_items(library_albums)

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
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    songs_removed = remove_library_items(library_songs)

    podcasts_removed, library_podcasts = remove_library_podcasts()

    items_removed = albums_removed + songs_removed + podcasts_removed

    items_total = len(library_albums) + len(library_songs) + len(library_podcasts)
    logging.info(f"Removed {items_removed} out of {items_total} albums, songs, and podcasts from your library.")
    return (items_removed, items_total)


def remove_library_podcasts():
    yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    logging.info("Retrieving all podcasts...")
    library_podcasts = yt_auth.get_library_podcasts(limit=None)
    # Filter out the "New Episodes" auto-playlist that can't be deleted
    library_podcasts = list(filter(lambda podcast: podcast["channel"]["id"], library_podcasts))
    logging.info(f"Retrieved {len(library_podcasts)} podcasts from your library.")
    global progress_bar
    progress_bar = manager.counter(
        total=len(library_podcasts),
        desc="Podcasts Removed",
        unit="podcasts",
        enabled=not get_current_context().obj["STATIC_PROGRESS"],
    )
    podcasts_removed = 0
    for podcast in library_podcasts:
        id = podcast.get("podcastId")
        title = podcast.get("title")
        if not id:
            logging.debug(f"\tCan't delete podcast {title!r} because it doesn't have an ID.")
            continue
        response = yt_auth.rate_playlist(id, common.INDIFFERENT)
        if "actions" in response:
            logging.info(f"\tRemoved {title!r} from your library.")
            podcasts_removed += 1
        else:
            logging.error(f"\tFailed to remove {title!r} from your library.")
        update_progress()
    logging.info(f"Removed {podcasts_removed} out of {len(library_podcasts)} podcasts from your library.")
    return podcasts_removed, library_podcasts


def remove_library_items(library_items):
    yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    items_removed = 0
    for item in library_items:
        logging.debug(f"Full album or song item: {item}")
        artist = (
            item["artists"][0]["name"]
            if item.get("artists")  # Using `get` ensures key exists and isn't []
            else common.UNKNOWN_ARTIST
        )
        title = item.get("title")
        logging.info(f"Processing item: {artist} - {title!r}")

        id = item.get("playlistId")
        response = None
        if id:
            logging.debug(f"Removing album using id: {id}")
            response = yt_auth.rate_playlist(id, common.INDIFFERENT)
        elif item.get("feedbackTokens") and isinstance(item.get("feedbackTokens"), dict):
            logging.debug("This is a song, removing item by removing containing album.")
            album_browse_id = item["album"]["id"]
            audio_playlist_id = common.get_album_audio_playlist_id(album_browse_id)
            response = None
            if audio_playlist_id:
                response = yt_auth.rate_playlist(audio_playlist_id, common.INDIFFERENT)
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
        update_progress()
    return items_removed


@cli.command()
@click.pass_context
def unlike_all(ctx: click.Context):
    """Reset all Thumbs Up ratings back to neutral"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    logging.info("Retrieving all your liked songs...")
    try:
        your_likes = yt_auth.get_liked_songs(limit=None)
    except Exception:
        logging.error("\tNo liked songs found or error retrieving liked songs.")
        raise
    logging.info(f"\tRetrieved {len(your_likes['tracks'])} liked songs.")
    logging.info("Begin unliking songs...")
    global progress_bar
    progress_bar = manager.counter(
        total=len(your_likes["tracks"]),
        desc="Songs Unliked",
        unit="songs",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    songs_unliked = 0
    for track in your_likes["tracks"]:
        artist = (
            track["artists"][0]["name"]
            if track.get("artists")  # Using `get` ensures key exists and isn't []
            else common.UNKNOWN_ARTIST
        )
        title = track["title"]
        logging.info(f"Processing track: {artist} - {title!r}")
        try:
            response = yt_auth.rate_song(track["videoId"], common.INDIFFERENT)
            num_retries = 300
            while num_retries > 0 and (
                not common.string_exists_in_dict(response, "Removed from liked music")
                or not common.string_exists_in_dict(response, "consistencyTokenJar")
            ):
                logging.info("\tRetrying track...")
                response = yt_auth.rate_song(track["videoId"], common.INDIFFERENT)
                num_retries -= 1
            if num_retries == 0:
                logging.error("\tRan out of retries to remove track from Likes. Try running 'Unlike All' again.")
            else:
                logging.info("\tRemoved track from Likes.")
                songs_unliked += 1
        except Exception as e:
            logging.exception(e)
            logging.error(f"\tFailed to unlike {artist} - {title!r}")
        update_progress()
    logging.info(f"Finished unliking {songs_unliked} out of {len(your_likes['tracks'])} songs.")
    return (songs_unliked, len(your_likes["tracks"]))


@cli.command()
@click.pass_context
def delete_playlists(ctx: click.Context):
    """Delete all playlists"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    logging.info("Retrieving all your playlists...")
    library_playlists = yt_auth.get_library_playlists(limit=None)
    # Can't delete "Your Likes" playlist
    library_playlists = list(filter(lambda playlist: playlist["playlistId"] != "LM", library_playlists))
    logging.info(f"\tRetrieved {len(library_playlists)} playlists.")
    logging.info("Begin deleting playlists...")
    global progress_bar
    progress_bar = manager.counter(
        total=len(library_playlists),
        desc="Playlists Deleted",
        unit="playlists",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    playlists_deleted = 0
    for playlist in library_playlists:
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
        update_progress()
    logging.info(f"Deleted {playlists_deleted} out of {len(library_playlists)} playlists from your library.")
    return (playlists_deleted, len(library_playlists))


@cli.command()
@click.pass_context
def delete_history(ctx: click.Context, items_deleted: int = 0):
    """
    Delete your play history. This does not currently work with brand accounts.
    The API can only retrieve 200 history items at a time, so the process will appear to
    start over and repeat multiple times if necessary until all history is deleted.
    """
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    logging.info("Begin deleting history...")
    try:
        history_items = yt_auth.get_history()
    except Exception as e:
        if str(e) == "None":
            logging.info("History is empty, nothing left to delete.")
        else:
            logging.exception(e)
        logging.info(f"Deleted {items_deleted} history items.")
        return items_deleted
    global progress_bar
    progress_bar = manager.counter(
        total=len(history_items),
        desc="History Items Deleted",
        unit="items",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    logging.info(f"Found {len(history_items)} history items to delete.")
    for item in history_items:
        artist = (
            item["artists"][0]["name"]
            if item.get("artists")  # Using `get` ensures key exists and isn't []
            else common.UNKNOWN_ARTIST
        )
        logging.info(f"\tProcessing history item: {artist} - {item['title']!r}")
        response = yt_auth.remove_history_items(item["feedbackToken"])
        if response.get("feedbackResponses")[0].get("isProcessed"):
            logging.info(f"\tDeleted history item: {artist} - {item['title']!r}")
            items_deleted += 1
        else:
            logging.info(f"\tFailed to delete history item: {response}")
        update_progress()
    logging.info("Restarting history deletion to ensure all songs are deleted.")
    time.sleep(5)  # Wait before checking for new items as they take time to disappear
    return ctx.invoke(delete_history, items_deleted)  # repeat until history is empty


@cli.command()
@click.pass_context
def delete_all(ctx: click.Context):
    """Executes delete-uploads, remove-library, delete-playlists, unlike-all, and delete-history"""
    ctx.invoke(delete_uploads)
    ctx.invoke(remove_library)
    ctx.invoke(delete_playlists)
    ctx.invoke(unlike_all)
    ctx.invoke(delete_history)


@cli.command()
@click.argument("playlist_titles", nargs=-1, required=True)
@click.option("--shuffle", "-s", is_flag=True, help="Shuffle the playlist(s) instead of sorting.")
@click.option("--custom-sort", "-c", multiple=True, metavar="ATTRIBUTE", help="Enable custom sorting")
@click.option("--reverse", "-r", is_flag=True, help="Reverse the entire playlist after sorting")
@click.pass_context
def sort_playlist(ctx: click.Context, shuffle, playlist_titles, custom_sort, reverse):
    """Sort or shuffle one or more playlists alphabetically by artist and by album"""
    invalid_keys = [attr for attr in custom_sort if attr not in common.SORTABLE_ATTRIBUTES]
    if invalid_keys:
        raise ValueError(f"Invalid sort option(s): {', '.join(invalid_keys)}")

    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    all_playlists = yt_auth.get_library_playlists(limit=None)
    lowercase_playlist_titles = [title.lower() for title in playlist_titles]
    selected_playlist_list = [
        playlist for playlist in all_playlists if playlist["title"].lower() in lowercase_playlist_titles
    ]
    for selected_playlist in selected_playlist_list:
        logging.info(f'Processing playlist: {selected_playlist["title"]}')
        playlist = yt_auth.get_playlist(selected_playlist["playlistId"], limit=None)
        if not common.can_edit_playlist(playlist):
            logging.error(f"Cannot modify playlist {playlist.get('title')!r}. You are not the owner of this playlist.")
            continue
        current_tracklist = [t for t in playlist["tracks"]]
        if shuffle:
            logging.info(f"\tPlaylist: {selected_playlist['title']} will be shuffled")
            desired_tracklist = [t for t in playlist["tracks"]]
            unsort(desired_tracklist)
        else:
            desired_tracklist = [
                t for t in sorted(playlist["tracks"], key=lambda t: make_sort_key(t, custom_sort), reverse=reverse)
            ]

        global progress_bar
        progress_bar = manager.counter(
            total=len(desired_tracklist),
            desc=f'{selected_playlist["title"]!r} Tracks {"Shuffled" if shuffle else "Sorted"}',
            unit="tracks",
            enabled=not ctx.obj["STATIC_PROGRESS"],
        )
        for cur_track in desired_tracklist:
            cur_idx = desired_tracklist.index(cur_track)
            track_after = current_tracklist[cur_idx]

            cur_artist = cur_track["artists"][0]["name"] if cur_track.get("artists") else common.UNKNOWN_ARTIST
            track_after_artist = (
                track_after["artists"][0]["name"]
                if track_after.get("artists")  # Using `get` ensures key exists and isn't []
                else common.UNKNOWN_ARTIST
            )
            if cur_track != track_after:
                logging.debug(
                    f"Moving {cur_artist} - {cur_track['title']!r} before {track_after_artist} - {track_after['title']!r}"
                )
                try:
                    if "setVideoId" not in cur_track or "setVideoId" not in track_after:
                        logging.error(
                            "Encountered track(s) with missing 'setVideoId'. Cannot sort the following track(s):"
                        )
                        if "setVideoId" not in cur_track:
                            logging.error(f"setVideoId attribute not in cur_track: {cur_track}")
                        if "setVideoId" not in track_after:
                            logging.error(f"setVideoId attribute not in track_after: {track_after}")
                        continue

                    response = yt_auth.edit_playlist(
                        playlist["id"],
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
                except Exception:
                    logging.error(
                        f"Failed to move {cur_artist} - {cur_track['title']!r} "
                        f"before {track_after_artist} - {track_after['title']!r}"
                    )

                current_tracklist.remove(cur_track)
                current_tracklist.insert(cur_idx, cur_track)
            update_progress()

    not_found_playlists = []
    for title in lowercase_playlist_titles:
        if title not in [x["title"].lower() for x in selected_playlist_list]:
            not_found_playlists.append(title)
    if not_found_playlists:
        raise click.BadParameter(
            f'No playlists found named {", ".join(not_found_playlists)!r}. Double-check your playlist name(s) '
            '(or surround them "with quotes") and try again.'
        )


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
        return tuple([locals()[attr] for attr in sort_attributes])
    else:
        return (artist, album_title, track_title)


@cli.command()
@click.argument("playlist_title")
@click.option("--exact", "-e", is_flag=True, help="Only remove exact duplicates")
@click.pass_context
def remove_duplicates(ctx: click.Context, playlist_title, exact):
    """Delete all duplicates in a given playlist"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    playlist = get_playlist_from_title(yt_auth, playlist_title)

    # Get a list of all the sets of duplicates
    duplicates = check_for_duplicates(playlist)
    if not duplicates:
        logging.info("No duplicates found. If you think this is an error open an issue on GitHub or message on Discord")
        return
    # For each dupe group, remove all but the first song
    items_to_remove, _ = determine_tracks_to_remove(duplicates)
    if not items_to_remove:
        logging.info("Finished: No duplicate tracks were marked for deletion.")
        return
    logging.info(f"Removing {len(items_to_remove)} tracks total.")
    playlist_id = playlist.get("id")
    if playlist_id == "LM":
        for song in items_to_remove:
            yt_auth.rate_song(song["videoId"], common.INDIFFERENT)
    else:
        yt_auth.remove_playlist_items(playlist_id, items_to_remove)
    logging.info("Finished removing duplicate tracks.")


@cli.command
@click.argument("playlist_title")
@click.option("--library", "-l", is_flag=True, help="Add all library songs to a playlist")
@click.option("--uploads", "-u", is_flag=True, help="Add all uploaded songs to a playlist")
@click.pass_context
def add_all_to_playlist(ctx: click.Context, playlist_title, library, uploads):
    """Add all library songs or uploaded songs to a playlist."""
    if not (library or uploads):
        raise click.BadParameter("You must specify either --library or --uploads.")

    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    playlist = get_playlist_from_title(yt_auth, playlist_title)
    if library:
        logging.info("User has selected 'Library' option. Retrieving all library songs...")
        library_songs = yt_auth.get_library_songs(limit=None)
        logging.info(f"Retrieved {len(library_songs)} library songs.")
        songs_to_add = library_songs
    elif uploads:
        logging.info("User has selected 'Uploads' option. Retriving all uploaded songs...")
        uploaded_songs = yt_auth.get_library_upload_songs(limit=None)
        logging.info(f"Retrieved {len(uploaded_songs)} uploaded songs.")
        songs_to_add = uploaded_songs

    if not songs_to_add:
        raise ValueError("No songs were found to add to the playlist.")

    video_ids = []
    for song in songs_to_add:
        if "videoId" in song:
            video_ids.append(song["videoId"])
        else:
            logging.warning(f"Warning: 'videoId' not found for {song.get('title')!r}, cannot add to playlist:", song)

    logging.info(f"Preparing to add all {len(video_ids)} songs to playlist {playlist.get('title')!r}.")
    response = yt_auth.add_playlist_items(playlist.get("id"), video_ids, duplicates=True)
    if "status" not in response or "STATUS_SUCCEEDED" not in response.get("status"):
        logging.error(response)
        raise RuntimeError("API did not return a success message. See response object above.")
    logging.info(f"Finished adding {len(video_ids)} songs to playlist {playlist.get('title')!r}.")


def get_playlist_from_title(yt_auth: YTMusic, playlist_title: str) -> dict:
    """
    Takes the given playlist title string and returns the full dict object for that playlist.
    Raises an error if the playlist is not modifiable.
    """
    # Get all playlists
    all_playlists = yt_auth.get_library_playlists(limit=None)
    # Get the ID of the matching playlist
    selected_playlist_id = next(
        (
            playlist["playlistId"]
            for playlist in all_playlists
            if playlist.get("title").lower() == playlist_title.lower()
        ),
        None,
    )
    if not selected_playlist_id:
        raise click.BadParameter(
            f"No playlist found named {playlist_title!r}. Double-check your playlist name "
            '(or surround it "with quotes") and try again.'
        )
    playlist: dict = yt_auth.get_playlist(selected_playlist_id, limit=None)
    playlist_title_formatted = playlist.get("title")
    logging.info(f"Retrieved playlist named {playlist_title_formatted!r} with {len(playlist.get('tracks'))} tracks.")
    if not common.can_edit_playlist(playlist):
        raise click.BadParameter(
            f"Cannot modify playlist {playlist_title_formatted!r}. You are not the owner of this playlist."
        )
    return playlist


def update_progress():
    global progress_bar
    progress_bar.update()
    if get_current_context().obj["STATIC_PROGRESS"]:
        logging.info(f"Total complete: {round(progress_bar.count / progress_bar.total * 100)}%")


if __name__ == "__main__":
    cli()
