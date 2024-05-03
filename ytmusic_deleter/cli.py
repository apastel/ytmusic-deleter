import logging
import os
import re
import sys
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from random import shuffle as unsort
from time import strftime

import click
from click import get_current_context
from ytmusic_deleter import constants as const
from ytmusic_deleter._version import __version__
from ytmusic_deleter.auth import ensure_auth
from ytmusic_deleter.progress import manager
from ytmusic_deleter.uploads import maybe_delete_uploaded_albums
from ytmusicapi import YTMusic


@click.group()
@click.version_option(__version__)
@click.option(
    "--log-dir",
    "-l",
    default=os.getcwd(),
    help="Custom directory in which to write log files, instead of current working directory.",
)
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
@click.pass_context
def cli(ctx, log_dir, credential_dir, static_progress):
    """Perform batch delete operations on your YouTube Music library."""

    logging.basicConfig(
        force=True,
        level=logging.INFO,
        format="[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(Path(log_dir) / f"ytmusic-deleter_{strftime('%Y-%m-%d')}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    if ctx.obj is not None:
        # Allows yt_auth to be provided by pytest
        yt_auth: YTMusic = ctx.obj
        logging.info(f"Logged in as {yt_auth.get_account_info().get('accountName')!r}")
    else:
        yt_auth: YTMusic = ensure_auth(credential_dir)
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
    "--fuzzy",
    "-f",
    is_flag=True,
    help="When using --add-to-library, this enables 'fuzzy' matching, allowing more flexibility when searching for matches among the YTM online catalog.",  # noqa: B950
)
@click.option(
    "--score-cutoff",
    "-s",
    default=90,
    help="When combined with the --add-to-library and --fuzzy flags, this optional integer argument between 0 and 100 is used when finding matches in the YTM online catalog. No matches with a score less than this number will be added to your library. Defaults to 90.",  # noqa: B950
)
@click.pass_context
def delete_uploads(ctx: click.Context, **kwargs):
    """Delete all songs that you have uploaded to your YT Music library."""
    (albums_deleted, albums_total) = maybe_delete_uploaded_albums()
    logging.info(f"Deleted {albums_deleted} out of {albums_total} uploaded albums (or songs).")
    remaining_count = albums_total - albums_deleted
    if (ctx.params["add_to_library"]) and remaining_count > 0:
        logging.info(
            f"\tRemaining {remaining_count} albums (or songs) did not have a match in YouTube Music's online catalog."
        )
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
    albums_removed = remove_library_albums(library_albums)

    logging.info("Retrieving all singles...")
    # Aside from actual singles, these might also be individual songs from an album that were added to your library
    try:
        library_songs = yt_auth.get_library_songs(limit=None)
        logging.info(f"Retrieved {len(library_songs)} singles from your library.")
    except Exception:
        logging.exception("Failed to get library singles.")
        library_songs = []
    # Filter out songs where album is None (rare but seen here: https://github.com/apastel/ytmusic-deleter/issues/12)
    filtered_songs = list(filter(lambda song: song["album"], library_songs))
    if len(library_songs) - len(filtered_songs) > 0:
        logging.info(f"{len(library_songs) - len(filtered_songs)} songs are not part of an album and won't be deleted.")
    # Filter for unique album IDs so that for each song, we can just remove the album it's a part of
    album_unique_songs = list({v["album"]["id"]: v for v in filtered_songs}.values())
    progress_bar = manager.counter(
        total=len(album_unique_songs),
        desc="Singles Processed",
        unit="singles",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    albums_removed += remove_library_albums_by_song(album_unique_songs)

    podcasts_removed, library_podcasts = remove_library_podcasts()

    albums_removed += podcasts_removed

    albums_total = len(library_albums) + len(album_unique_songs) + len(library_podcasts)
    logging.info(f"Removed {albums_removed} out of {albums_total} albums and podcasts from your library.")
    return (albums_removed, albums_total)


def remove_library_podcasts():
    yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    logging.info("Retreiving all podcasts...")
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
        if not id:
            logging.debug(f"\tCan't delete podcast {podcast.get('title')!r} because it doesn't have an ID.")
            continue
        response = yt_auth.rate_playlist(id, const.INDIFFERENT)
        if "actions" in response:
            logging.info(f"\tRemoved {podcast.get('title')!r} from your library.")
            podcasts_removed += 1
        else:
            logging.error(f"\tFailed to remove {podcast.get('title')!r} from your library.")
        update_progress()
    logging.info(f"Removed {podcasts_removed} out of {len(library_podcasts)} podcasts from your library.")
    return podcasts_removed, library_podcasts


def remove_library_albums(albums):
    albums_removed = 0
    for album in albums:
        if remove_album(album["browseId"]):
            albums_removed += 1
        update_progress()
    return albums_removed


def remove_library_albums_by_song(songs):
    albums_removed = 0
    for song in songs:
        if remove_album(song["album"]["id"]):
            albums_removed += 1
        update_progress()
    return albums_removed


def remove_album(browseId):
    yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    try:
        album = yt_auth.get_album(browseId)
    except Exception:
        logging.exception(
            f"\tFailed to remove album with ID {browseId} from your library, as it could not be retrieved."
        )
        return False
    artist = album["artists"][0]["name"] if "artists" in album else const.UNKNOWN_ARTIST
    title = album["title"]
    logging.info(f"Processing album: {artist} - {title}")
    response = yt_auth.rate_playlist(album["audioPlaylistId"], const.INDIFFERENT)
    if response:
        logging.info(f"\tRemoved {artist} - {title} from your library.")
        return True
    else:
        logging.error(f"\tFailed to remove {artist} - {title} from your library.")
        return False


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
            else const.UNKNOWN_ARTIST
        )
        title = track["title"]
        logging.info(f"Processing track: {artist} - {title}")
        if track["album"] is None:
            logging.info("\tSkipping unliking as this might be a YouTube video and not a YouTube Music song.")
        else:
            logging.info("\tRemoved track from Likes.")
            yt_auth.rate_song(track["videoId"], const.INDIFFERENT)
            songs_unliked += 1
        update_progress()
    logging.info("Finished unliking all songs.")
    return (songs_unliked, len(your_likes["tracks"]))


@cli.command()
@click.pass_context
def delete_playlists(ctx: click.Context):
    """Delete all playlists"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    logging.info("Retrieving all your playlists...")
    library_playlists = yt_auth.get_library_playlists(sys.maxsize)
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
            logging.error(f"\tCould not delete playlist {playlist['title']}. It might be a YT Music curated playlist.")
        update_progress()
    logging.info(f"Deleted {playlists_deleted} out of {len(library_playlists)} from your library.")
    return (playlists_deleted, len(library_playlists))


@cli.command()
@click.pass_context
def delete_history(ctx: click.Context):
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
            logging.info("History is empty, nothing to delete.")
        else:
            logging.exception(e)
        return False
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
            else const.UNKNOWN_ARTIST
        )
        logging.info(f"Processing {artist} - {item['title']}")
        yt_auth.remove_history_items(item["feedbackToken"])
        update_progress()
    ctx.invoke(delete_history)  # repeat until history is empty


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
@click.pass_context
def sort_playlist(ctx: click.Context, shuffle, playlist_titles):
    """Sort or shuffle one or more playlists alphabetically by artist and by album"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
    all_playlists = yt_auth.get_library_playlists(sys.maxsize)
    lowercase_playlist_titles = [title.lower() for title in playlist_titles]
    selected_playlist_list = [
        playlist for playlist in all_playlists if playlist["title"].lower() in lowercase_playlist_titles
    ]
    for selected_playlist in selected_playlist_list:
        logging.info(f'Processing playlist: {selected_playlist["title"]}')
        playlist = yt_auth.get_playlist(selected_playlist["playlistId"], sys.maxsize)
        current_tracklist = [t for t in playlist["tracks"]]
        if shuffle:
            logging.info(f"\tPlaylist: {selected_playlist['title']} will be shuffled")
            desired_tracklist = [t for t in playlist["tracks"]]
            unsort(desired_tracklist)
        else:
            desired_tracklist = [t for t in sorted(playlist["tracks"], key=lambda t: make_sort_key(t))]

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
            logging.debug(  # No way to actually enable debug logging yet
                f"Moving {cur_track['artists'][0]['name']} - {cur_track['title']} "
                f"before {track_after['artists'][0]['name']} - {track_after['title']}"
            )
            if cur_track != track_after:
                try:
                    response = yt_auth.edit_playlist(
                        playlist["id"],
                        moveItem=(
                            cur_track["setVideoId"],
                            track_after["setVideoId"],
                        ),
                    )
                    if not response:
                        logging.error(
                            f"Failed to move {cur_track['artists'][0]['name']} - {cur_track['title']} "
                            f"before {track_after['artists'][0]['name']} - {track_after['title']}"
                        )
                except Exception:
                    logging.error(
                        f"Failed to move {cur_track['artists'][0]['name']} - {cur_track['title']} "
                        f"before {track_after['artists'][0]['name']} - {track_after['title']}"
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


def make_sort_key(track):
    try:
        artists = track["artists"]
        artist = artists[0]["name"].lower() if artists else "z"
        album = track["album"]
        album_title = album["name"] if album else "z"
        return (re.sub(r"^(the |a )", "", artist), album_title, track["title"])
    except Exception:
        logging.exception(f"Track {track} could not be sorted.")
        raise


@cli.command()
@click.argument("playlist_title")
@click.pass_context
def remove_duplicates(ctx: click.Context, playlist_title):
    """Delete all duplicates in a given playlist"""
    yt_auth: YTMusic = ctx.obj["YT_AUTH"]
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
    # Get a list of all the sets of duplicates
    duplicates = check_for_duplicates(selected_playlist_id)
    if not duplicates:
        logging.info("No duplicates found. If you think this is an error open an issue on GitHub or message on Discord")
    # For each dupe group, remove all but the first song
    for duplicate_group in duplicates:
        master_track = duplicate_group[0]
        logging.info(
            f"The following track(s) are a duplicate of {master_track.get('artist')} - {master_track.get('title')!r} "
            "and will be removed:"
        )
        items_to_remove = duplicate_group[1:]
        for item in items_to_remove:
            logging.info(f"\t{item.get('artist')} - {item.get('title')!r}")
        yt_auth.remove_playlist_items(selected_playlist_id, items_to_remove)


def check_for_duplicates(playlist_id: str, yt_auth: YTMusic = None):
    # Allow passing in yt_auth from pytest
    if not yt_auth:
        yt_auth: YTMusic = get_current_context().obj["YT_AUTH"]
    # Get the playlist object
    playlist = yt_auth.get_playlist(playlist_id)
    logging.info(f"Checking for duplicates in playlist {playlist.get('title')!r}")
    tracks = playlist.get("tracks")
    # Trim the fat of the tracks object
    tracks = [
        {
            "artist": track.get("artists")[0].get("name"),
            "title": track.get("title"),
            "videoId": track.get("videoId"),
            "setVideoId": track.get("setVideoId"),
        }
        for track in tracks
    ]

    # Create a list of groups of duplicate tracks, where dupes are determined by having the same videoId
    tracks.sort(key=itemgetter("videoId"))
    grouped_tracks = [(key, list(group)) for key, group in groupby(tracks, lambda item: item["videoId"])]
    grouped_tracks = [group for key, group in grouped_tracks if len(group) > 1]

    return grouped_tracks


def update_progress():
    global progress_bar
    progress_bar.update()
    if get_current_context().obj["STATIC_PROGRESS"]:
        logging.info(f"Total complete: {round(progress_bar.count / progress_bar.total * 100)}%")


if __name__ == "__main__":
    cli()
