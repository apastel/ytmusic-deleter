from ytmusicapi import YTMusic
from ytmusic_deleter import constants as const
import click
import logging
import sys
import enlighten

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    handlers=[logging.FileHandler("ytmusic-deleter.log"),
                              logging.StreamHandler(sys.stdout)])


def get_auth_obj():
    auth_obj = None
    try:
        auth_obj = YTMusic(const.HEADERS_FILE)
    except (KeyError, AttributeError):
        logging.info(f"Creating {const.HEADERS_FILE} file...")
        auth_obj = YTMusic(YTMusic.setup(filepath=const.HEADERS_FILE))

    return auth_obj


youtube_auth = get_auth_obj()
manager = enlighten.get_manager()


@click.group()
def cli():
    """Perform batch delete operations on your YouTube Music library.
    """


@cli.command()
@click.option("--add-to-library",
              "-a",
              is_flag=True,
              help="Add corresponding albums to your library before deleting them from uploads.")
def delete_uploads(add_to_library):
    """Delete all tracks that you have uploaded to your YT Music library.
    """
    (albums_deleted, albums_total) = delete_uploaded_albums(add_to_library)
    logging.info(f"Deleted {albums_deleted} out of {albums_total} uploaded albums.")
    if (add_to_library) and albums_total - albums_deleted > 0:
        logging.info(
            f"\tRemaining {albums_total - albums_deleted} did not have a match in YouTube Music's online catalog.")

    (songs_deleted, songs_total) = delete_uploaded_songs()
    logging.info(f"Deleted {songs_deleted} out of {songs_total} uploaded songs that are not part of an album.")


def delete_uploaded_albums(add_to_library):
    logging.info("Retrieving all uploaded albums...")
    albums_deleted = 0
    uploaded_albums = youtube_auth.get_library_upload_albums(sys.maxsize)
    if not uploaded_albums:
        return (albums_deleted, 0)
    progress_bar = manager.counter(total=len(uploaded_albums), desc="Albums Processed", unit="albums")
    for album in uploaded_albums:
        try:
            artist = album["artists"][0]["name"] if album["artists"] else "Unknown Artist"
            title = album["title"]
            logging.info(f"Processing album: {artist} - {title}")
            if add_to_library and not add_album_to_library(artist, title):
                logging.warn("\tNo match for uploaded album found in online catalog. Will not delete.")
                progress_bar.update()
                continue
            response = youtube_auth.delete_upload_entity(album["browseId"])
            if response == "STATUS_SUCCEEDED":
                logging.info("\tDeleted album from uploads.")
                albums_deleted += 1
            else:
                logging.error("\tFailed to delete album from uploads")
        except (AttributeError, TypeError, KeyError) as e:
            logging.error(e)
        progress_bar.update()
    return (albums_deleted, len(uploaded_albums))


def delete_uploaded_songs():
    logging.info("Retrieving all uploaded songs that are not part of an album...")
    songs_deleted = 0
    uploaded_songs = youtube_auth.get_library_upload_songs(sys.maxsize)
    if not uploaded_songs:
        return (songs_deleted, 0)

    # Filter for songs that don"t have an album, otherwise songs that
    # were skipped in the first batch would get deleted here
    uploaded_songs = [song for song in uploaded_songs if not song["album"]]

    progress_bar = manager.counter(total=len(uploaded_songs), desc="Songs Processed", unit="songs")

    for song in uploaded_songs:
        try:
            artist = song["artist"][0]["name"] if song["artist"] else "Unknown Artist"
            title = song["title"]
            response = youtube_auth.delete_upload_entity(song["entityId"])
            if response == "STATUS_SUCCEEDED":
                logging.info(f"\tDeleted {artist} - {title}")
                songs_deleted += 1
            else:
                logging.error(f"\tFailed to delete {artist} - {title}")
        except (AttributeError, TypeError) as e:
            logging.error(e)
        progress_bar.update()

    return (songs_deleted, len(uploaded_songs))


def add_album_to_library(artist, title):
    logging.info("\tSearching for album in online catalog...")
    search_results = youtube_auth.search(f"{artist} {title}")
    for result in search_results:
        # Find the first album for which the artist and album title are substrings
        if result["resultType"] == "album" and artist.lower() in str(result["artist"]).lower() and title.lower() in str(
                result["title"]).lower():
            catalog_album = youtube_auth.get_album(result["browseId"])
            logging.info(f"\tFound matching album \"{catalog_album['title']}\" in YouTube Music. Adding to library...")
            for track in catalog_album["tracks"]:
                youtube_auth.rate_song(track["videoId"], const.LIKE)
            logging.info("\tAdded album to library.")
            return True
    return False


@cli.command()
def remove_library():
    """Remove all tracks that you have added to your library from within YouTube Music.
    """
    logging.info("Retrieving all library albums...")
    try:
        library_albums = youtube_auth.get_library_albums(sys.maxsize)
        logging.info(f"Retrieved {len(library_albums)} albums from your library.")
    except Exception:
        logging.exception("Failed to get library albums.")
        library_albums = []
    progress_bar = manager.counter(total=len(library_albums), desc="Albums Processed", unit="albums")
    albums_removed = remove_library_albums(library_albums, progress_bar)

    logging.info("Retrieving all singles...")
    try:
        library_songs = youtube_auth.get_library_songs(sys.maxsize)
        logging.info(f"Retrieved {len(library_songs)} singles from your library.")
    except Exception:
        logging.exception("Failed to get library singles.")
        library_songs = []
    # Filter for unique album IDs
    filtered_songs = list({v["album"]["id"]: v for v in library_songs}.values())
    progress_bar = manager.counter(total=len(filtered_songs), desc="Singles Processed", unit="singles")
    albums_removed += remove_library_albums_by_song(filtered_songs, progress_bar)
    logging.info(
        f"Removed {albums_removed} out of {len(library_albums) + len(filtered_songs)} albums from your library.")


def remove_library_albums(albums, progress_bar):
    albums_removed = 0
    for album in albums:
        if remove_album(album["browseId"]):
            albums_removed += 1
        progress_bar.update()
    return albums_removed


def remove_library_albums_by_song(songs, progress_bar):
    albums_removed = 0
    for song in songs:
        if remove_album(song["album"]["id"]):
            albums_removed += 1
        progress_bar.update()
    return albums_removed


def remove_album(browseId):
    try:
        album = youtube_auth.get_album(browseId)
    except Exception:
        logging.exception(
            f"\tFailed to remove album with ID {browseId} from your library, as it could not be retrieved.")
        return False
    artist = album["artist"][0]["name"] if album["artist"] else "Unknown Artist"
    title = album["title"]
    logging.info(f"Processing album: {artist} - {title}")
    response = youtube_auth.rate_playlist(album["playlistId"], const.INDIFFERENT)
    if response:
        logging.info(f"\tRemoved {artist} - {title} from your library.")
        return True
    else:
        logging.error(f"\tFailed to remove {artist} - {title} from your library.")
        return False


@cli.command()
@click.pass_context
def delete_all(ctx):
    """Executes delete-uploads and remove-library"""
    ctx.invoke(delete_uploads)
    ctx.invoke(remove_library)
