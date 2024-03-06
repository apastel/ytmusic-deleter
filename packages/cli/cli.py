import logging
import os
import re
import sys
from json import JSONDecodeError
from pathlib import Path
from random import shuffle as unsort
from time import strftime

import click
import enlighten
import ytmusicapi
import constants as const
from ytmusicapi import YTMusic

manager = enlighten.get_manager()
progress_bar = None


def ensure_auth(credential_dir):
    global youtube_auth
    oauth_file_path: str = str(Path(credential_dir) / const.OAUTH_FILENAME)
    try:
        logging.info(f"Attempting authentication with: {oauth_file_path}")
        youtube_auth = YTMusic(oauth_file_path)
        logging.info(f'Authenticated with: {oauth_file_path}"')
    except JSONDecodeError:
        logging.info(f"Creating file: {const.OAUTH_FILENAME}")
        ytmusicapi.setup_oauth(filepath=oauth_file_path, open_browser=True)
        youtube_auth = YTMusic(oauth_file_path)
        logging.info(f'Created: {oauth_file_path}"')
    finally:
        logging.info(f"Logged in as {youtube_auth.get_account_info().get('accountName')!r}")


@click.group()
@click.version_option(package_name="ytmusic-deleter")
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
            logging.FileHandler(
                Path(log_dir) / f"ytmusic-deleter_{strftime('%Y-%m-%d')}.log"
            ),
            logging.StreamHandler(sys.stdout),
        ],
    )
    ensure_auth(credential_dir)
    ctx.ensure_object(dict)
    ctx.obj["STATIC_PROGRESS"] = static_progress


@cli.command()
@click.option(
    "--add-to-library",
    "-a",
    is_flag=True,
    help="Add corresponding albums to your library before deleting them from uploads.",
)
@click.pass_context
def delete_uploads(ctx, add_to_library):
    """Delete all tracks that you have uploaded to your YT Music library."""
    (albums_deleted, albums_total) = delete_uploaded_albums(ctx, add_to_library)
    logging.info(f"Deleted {albums_deleted} out of {albums_total} uploaded albums.")
    if (add_to_library) and albums_total - albums_deleted > 0:
        logging.info(
            f"\tRemaining {albums_total - albums_deleted} albums did not have a match in YouTube Music's online catalog."
        )

    (singles_deleted, singles_total) = delete_uploaded_singles(ctx)
    logging.info(f"Deleted {singles_deleted} out of {singles_total} uploaded singles.")


def delete_uploaded_albums(ctx, add_to_library):
    logging.info("Retrieving all uploaded albums...")
    albums_deleted = 0
    uploaded_albums = youtube_auth.get_library_upload_albums(sys.maxsize)
    if not uploaded_albums:
        return (albums_deleted, 0)
    logging.info(f"Retrieved {len(uploaded_albums)} uploaded albums from your library.")

    global progress_bar
    progress_bar = manager.counter(
        total=len(uploaded_albums),
        desc="Albums Processed",
        unit="albums",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    for album in uploaded_albums:
        try:
            artist = (
                album["artists"][0]["name"]
                if album.get("artists")  # Using `get` ensures key exists and isn't []
                else const.UNKNOWN_ARTIST
            )
            title = album["title"]
            logging.info(f"Processing album: {artist} - {title}")
            if add_to_library:
                if artist == const.UNKNOWN_ARTIST:
                    logging.warn(
                        "\tAlbum is missing artist metadata. Skipping match search and will not delete."
                    )
                    update_progress(ctx)
                    continue
                elif not add_album_to_library(artist, title):
                    logging.warn(
                        "\tNo match for uploaded album found in online catalog. Will not delete."
                    )
                    update_progress(ctx)
                    continue
            response = youtube_auth.delete_upload_entity(album["browseId"])
            if response == "STATUS_SUCCEEDED":
                logging.info("\tDeleted album from uploads.")
                albums_deleted += 1
            else:
                logging.error("\tFailed to delete album from uploads")
        except (AttributeError, TypeError, KeyError) as e:
            logging.error(f"\tEncountered exception processing album attribute: {e}")
        update_progress(ctx)
    return (albums_deleted, len(uploaded_albums))


def delete_uploaded_singles(ctx):
    logging.info("Retrieving all uploaded singles...")
    singles_deleted = 0
    uploaded_singles = youtube_auth.get_library_upload_songs(sys.maxsize)
    if not uploaded_singles:
        return (singles_deleted, 0)

    # Filter for songs that don't have an album, otherwise songs that
    # were skipped in the first batch would get deleted here
    uploaded_singles = [single for single in uploaded_singles if not single["album"]]
    logging.info(
        f"Retrieved {len(uploaded_singles)} uploaded singles from your library."
    )

    global progress_bar
    progress_bar = manager.counter(
        total=len(uploaded_singles),
        desc="Singles Processed",
        unit="singles",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )

    for single in uploaded_singles:
        try:
            artist = (
                single["artist"][0]["name"]
                if single.get("artist")  # Using `get` ensures key exists and isn't []
                else const.UNKNOWN_ARTIST
            )
            title = single["title"]
            response = youtube_auth.delete_upload_entity(single["entityId"])
            if response == "STATUS_SUCCEEDED":
                logging.info(f"\tDeleted {artist} - {title}")
                singles_deleted += 1
            else:
                logging.error(f"\tFailed to delete {artist} - {title}")
        except (AttributeError, TypeError) as e:
            logging.error(e)
        update_progress(ctx)

    return (singles_deleted, len(uploaded_singles))


def add_album_to_library(artist, title):
    logging.info("\tSearching for album in online catalog...")
    search_results = youtube_auth.search(f"{artist} {title}")
    for result in search_results:
        # Find the first album for which the artist and album title are substrings
        if result["resultType"] == "album" and match_found(result, artist, title):
            catalog_album = youtube_auth.get_album(result["browseId"])
            logging.info(
                f"\tFound matching album \"{catalog_album['artist'][0]['name'] if 'artist' in catalog_album else ''}"
                f" - {catalog_album['title']}\" in YouTube Music. Adding to library..."
            )
            success = youtube_auth.rate_playlist(
                catalog_album["audioPlaylistId"], const.LIKE
            )
            if success:
                logging.info("\tAdded album to library.")
            else:
                logging.error("\tFailed to add album to library")
            return True
    return False


def match_found(result, artist, title):
    try:
        resultArtist = str(result["artist"]).lower()
    except KeyError:
        resultArtist = str(result["artists"][0] if "artists" in result else "").lower()
    try:
        resultTitle = str(result["title"]).lower()
    except KeyError:
        resultTitle = ""
    artist = artist.lower()
    title = title.lower()

    if artist in resultArtist and title in resultTitle:
        return True
    else:
        # Try again but strip out parentheticals and quotes
        resultTitle = re.sub(r"\(.*?\)|\[.*?\]|\"|\'", "", resultTitle).strip()
        title = re.sub(r"\(.*?\)|\[.*?\]|\"|\'", "", title).strip()
        return artist in resultArtist and title in resultTitle


@cli.command()
@click.pass_context
def remove_library(ctx):
    """Remove all tracks that you have added to your library from within YouTube Music."""
    logging.info("Retrieving all library albums...")
    try:
        library_albums = youtube_auth.get_library_albums(sys.maxsize)
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
    albums_removed = remove_library_albums(ctx, library_albums)

    logging.info("Retrieving all singles...")
    # Aside from actual singles, these might also be individual songs from an album that were added to your library
    try:
        library_songs = youtube_auth.get_library_songs(sys.maxsize)
        logging.info(f"Retrieved {len(library_songs)} singles from your library.")
    except Exception:
        logging.exception("Failed to get library singles.")
        library_songs = []
    # Filter out songs where album is None (rare but seen here: https://github.com/apastel/ytmusic-deleter/issues/12)
    filtered_songs = list(filter(lambda song: song["album"], library_songs))
    if len(library_songs) - len(filtered_songs) > 0:
        logging.info(
            f"{len(library_songs) - len(filtered_songs)} songs are not part of an album and won't be deleted."
        )
    # Filter for unique album IDs so that for each song, we can just remove the album it's a part of
    album_unique_songs = list({v["album"]["id"]: v for v in filtered_songs}.values())
    progress_bar = manager.counter(
        total=len(album_unique_songs),
        desc="Singles Processed",
        unit="singles",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    albums_removed += remove_library_albums_by_song(ctx, album_unique_songs)
    logging.info(
        f"Removed {albums_removed} out of {len(library_albums) + len(album_unique_songs)} albums from your library."
    )


def remove_library_albums(ctx, albums):
    albums_removed = 0
    for album in albums:
        if remove_album(album["browseId"]):
            albums_removed += 1
        update_progress(ctx)
    return albums_removed


def remove_library_albums_by_song(ctx, songs):
    albums_removed = 0
    for song in songs:
        if remove_album(song["album"]["id"]):
            albums_removed += 1
        update_progress(ctx)
    return albums_removed


def remove_album(browseId):
    try:
        album = youtube_auth.get_album(browseId)
    except Exception:
        logging.exception(
            f"\tFailed to remove album with ID {browseId} from your library, as it could not be retrieved."
        )
        return False
    artist = album["artists"][0]["name"] if "artists" in album else const.UNKNOWN_ARTIST
    title = album["title"]
    logging.info(f"Processing album: {artist} - {title}")
    response = youtube_auth.rate_playlist(album["audioPlaylistId"], const.INDIFFERENT)
    if response:
        logging.info(f"\tRemoved {artist} - {title} from your library.")
        return True
    else:
        logging.error(f"\tFailed to remove {artist} - {title} from your library.")
        return False


@cli.command()
@click.pass_context
def unlike_all(ctx):
    """Reset all Thumbs Up ratings back to neutral"""
    logging.info("Retrieving all your liked songs...")
    try:
        your_likes = youtube_auth.get_liked_songs(sys.maxsize)
    except Exception:
        logging.error("\tNo liked songs found or error retrieving liked songs.")
        return False
    logging.info(f"\tRetrieved {len(your_likes['tracks'])} liked songs.")
    logging.info("Begin unliking songs...")
    global progress_bar
    progress_bar = manager.counter(
        total=len(your_likes["tracks"]),
        desc="Songs Unliked",
        unit="songs",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    for track in your_likes["tracks"]:
        artist = (
            track["artists"][0]["name"]
            if track.get("artists")  # Using `get` ensures key exists and isn't []
            else const.UNKNOWN_ARTIST
        )
        title = track["title"]
        logging.info(f"Processing track: {artist} - {title}")
        if track["album"] is None:
            logging.info(
                "\tSkipping deletion as this might be a YouTube video and not a YouTube Music song."
            )
        else:
            logging.info("\tRemoved track from Likes.")
            youtube_auth.rate_song(track["videoId"], const.INDIFFERENT)
        update_progress(ctx)
    logging.info("Finished unliking all songs.")


@cli.command()
@click.pass_context
def delete_playlists(ctx):
    """Delete all playlists"""
    logging.info("Retrieving all your playlists...")
    library_playlists = youtube_auth.get_library_playlists(sys.maxsize)
    # Can't delete "Your Likes" playlist
    library_playlists = list(
        filter(lambda playlist: playlist["playlistId"] != "LM", library_playlists)
    )
    logging.info(f"\tRetrieved {len(library_playlists)} playlists.")
    logging.info("Begin deleting playlists...")
    global progress_bar
    progress_bar = manager.counter(
        total=len(library_playlists),
        desc="Playlists Deleted",
        unit="playlists",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    for playlist in library_playlists:
        logging.info(f"Processing playlist: {playlist['title']}")
        try:
            response = youtube_auth.delete_playlist(playlist["playlistId"])
            if response:
                logging.info(
                    f"\tRemoved playlist {playlist['title']!r} from your library."
                )
            else:
                logging.error(
                    f"\tFailed to remove playlist {playlist['title']!r} from your library."
                )
        except Exception:
            logging.error(
                f"\tCould not delete playlist {playlist['title']}. It might be a YT Music curated playlist."
            )
        update_progress(ctx)
    logging.info("Finished deleting all playlists")


@cli.command()
@click.pass_context
def delete_history(ctx):
    """
    Delete your play history. This does not currently work with brand accounts.
    The API can only retrieve 200 history items at a time, so the process will appear to
    start over and repeat multiple times if necessary until all history is deleted.
    """
    logging.info("Begin deleting history...")
    try:
        history_items = youtube_auth.get_history()
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
        youtube_auth.remove_history_items(item["feedbackToken"])
        update_progress(ctx)
    ctx.invoke(delete_history)  # repeat until history is empty


@cli.command()
@click.pass_context
def delete_all(ctx):
    """Executes delete-uploads, remove-library, delete-playlists, unlike-all, and delete-history"""
    ctx.invoke(delete_uploads)
    ctx.invoke(remove_library)
    ctx.invoke(delete_playlists)
    ctx.invoke(unlike_all)
    ctx.invoke(delete_history)


@cli.command()
@click.argument("playlist_titles", nargs=-1, required=True)
@click.option(
    "--shuffle", "-s", is_flag=True, help="Shuffle the playlist(s) instead of sorting."
)
@click.pass_context
def sort_playlist(ctx, shuffle, playlist_titles):
    """Sort or shuffle one or more playlists alphabetically by artist and by album"""
    all_playlists = youtube_auth.get_library_playlists(sys.maxsize)
    lowercase_playlist_titles = [title.lower() for title in playlist_titles]
    selected_playlist_list = [
        playlist
        for playlist in all_playlists
        if playlist["title"].lower() in lowercase_playlist_titles
    ]
    for selected_playlist in selected_playlist_list:
        logging.info(f'Processing crap: {selected_playlist["title"]}')
        playlist = youtube_auth.get_playlist(
            selected_playlist["playlistId"], sys.maxsize
        )
        current_tracklist = [t for t in playlist["tracks"]]
        if shuffle:
            logging.info(f"\tPlaylist: {selected_playlist['title']} will be shuffled")
            desired_tracklist = [t for t in playlist["tracks"]]
            unsort(desired_tracklist)
        else:
            desired_tracklist = [
                t for t in sorted(playlist["tracks"], key=lambda t: make_sort_key(t))
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
            logging.debug(  # No way to actually enable debug logging yet
                f"Moving {cur_track['artists'][0]['name']} - {cur_track['title']} "
                f"before {track_after['artists'][0]['name']} - {track_after['title']}"
            )
            if cur_track != track_after:
                try:
                    response = youtube_auth.edit_playlist(
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
            update_progress(ctx)

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


def update_progress(ctx):
    global progress_bar
    progress_bar.update()
    if ctx.obj["STATIC_PROGRESS"]:
        logging.info(
            f"Total complete: {round(progress_bar.count / progress_bar.total * 100)}%"
        )


if __name__ == "__main__":
    cli()
