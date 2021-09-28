from ytmusicapi import YTMusic
from ytmusic_deleter import constants as const
import click
import logging
import sys
import re
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
@click.version_option()
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
            f"\tRemaining {albums_total - albums_deleted} albums did not have a match in YouTube Music's online catalog."
        )

    (singles_deleted, singles_total) = delete_uploaded_singles()
    logging.info(f"Deleted {singles_deleted} out of {singles_total} uploaded singles.")


def delete_uploaded_albums(add_to_library):
    logging.info("Retrieving all uploaded albums...")
    albums_deleted = 0
    uploaded_albums = youtube_auth.get_library_upload_albums(sys.maxsize)
    if not uploaded_albums:
        return (albums_deleted, 0)
    progress_bar = manager.counter(total=len(uploaded_albums), desc="Albums Processed", unit="albums")
    for album in uploaded_albums:
        try:
            artist = album["artists"][0]["name"] if "artists" in album else const.UNKNOWN_ARTIST
            title = album["title"]
            logging.info(f"Processing album: {artist} - {title}")
            if add_to_library:
                if artist == const.UNKNOWN_ARTIST:
                    logging.warn("\tAlbum is missing artist metadata. Skipping match search and will not delete.")
                    progress_bar.update()
                    continue
                elif not add_album_to_library(artist, title):
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
            logging.error(f"\tEncountered exception processing album attribute: {e}")
        progress_bar.update()
    return (albums_deleted, len(uploaded_albums))


def delete_uploaded_singles():
    logging.info("Retrieving all uploaded singles...")
    singles_deleted = 0
    uploaded_singles = youtube_auth.get_library_upload_songs(sys.maxsize)
    if not uploaded_singles:
        return (singles_deleted, 0)

    # Filter for songs that don't have an album, otherwise songs that
    # were skipped in the first batch would get deleted here
    uploaded_singles = [single for single in uploaded_singles if not single["album"]]

    progress_bar = manager.counter(total=len(uploaded_singles), desc="Singles Processed", unit="singles")

    for single in uploaded_singles:
        try:
            artist = single["artist"][0]["name"] if "artist" in single else const.UNKNOWN_ARTIST
            title = single["title"]
            response = youtube_auth.delete_upload_entity(single["entityId"])
            if response == "STATUS_SUCCEEDED":
                logging.info(f"\tDeleted {artist} - {title}")
                singles_deleted += 1
            else:
                logging.error(f"\tFailed to delete {artist} - {title}")
        except (AttributeError, TypeError) as e:
            logging.error(e)
        progress_bar.update()

    return (singles_deleted, len(uploaded_singles))


def add_album_to_library(artist, title):
    logging.info("\tSearching for album in online catalog...")
    search_results = youtube_auth.search(f"{artist} {title}")
    for result in search_results:
        # Find the first album for which the artist and album title are substrings
        if result["resultType"] == "album" and match_found(result, artist, title):
            catalog_album = youtube_auth.get_album(result["browseId"])
            logging.info(
                f"\tFound matching album \"{catalog_album['artist'][0]['name'] if 'artist' in catalog_album else ''} - {catalog_album['title']}\" in YouTube Music. Adding to library..."
            )
            success = youtube_auth.rate_playlist(catalog_album["audioPlaylistId"], const.LIKE)
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
    # Aside from actual singles, these might also be individual songs from an album that were added to your library
    try:
        library_songs = youtube_auth.get_library_songs(sys.maxsize)
        logging.info(f"Retrieved {len(library_songs)} singles from your library.")
    except Exception:
        logging.exception("Failed to get library singles.")
        library_songs = []
    # Filter out songs where album is None (possible rare occurrence seen here: https://github.com/apastel/ytmusic-deleter/issues/12)
    filtered_songs = list(filter(lambda song: song["album"], library_songs))
    if len(library_songs) - len(filtered_songs) > 0:
        logging.info(f"{len(library_songs) - len(filtered_songs)} songs are not part of an album and won't be deleted.")
    # Filter for unique album IDs so that for each song, we can just remove the album it's a part of
    album_unique_songs = list({v["album"]["id"]: v for v in filtered_songs}.values())
    progress_bar = manager.counter(total=len(album_unique_songs), desc="Singles Processed", unit="singles")
    albums_removed += remove_library_albums_by_song(album_unique_songs, progress_bar)
    logging.info(
        f"Removed {albums_removed} out of {len(library_albums) + len(album_unique_songs)} albums from your library.")


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
    artist = album["artist"][0]["name"] if "artist" in album else const.UNKNOWN_ARTIST
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
def unlike_all():
    """Reset all Thumbs Up ratings back to neutral
    """
    logging.info("Retrieving all your liked songs...")
    try:
        your_likes = youtube_auth.get_liked_songs(sys.maxsize)
    except Exception:
        logging.error("\tNo liked songs found or error retrieving liked songs.")
        return False
    logging.info(f"\tRetrieved {len(your_likes['tracks'])} liked songs.")
    logging.info("Begin unliking songs...")
    progress_bar = manager.counter(total=len(your_likes['tracks']), desc="Songs Unliked", unit="songs")
    for track in your_likes["tracks"]:
        artist = track["artists"][0]["name"] if "artists" in track else const.UNKNOWN_ARTIST
        title = track["title"]
        logging.info(f"Processing track: {artist} - {title}")
        if track["album"] is None:
            logging.info("\tSkipping deletion as this might be a YouTube video and not a YouTube Music song.")
        else:
            logging.info("\tRemoved track from Likes.")
            youtube_auth.rate_song(track["videoId"], const.INDIFFERENT)
        progress_bar.update()
    logging.info("Finished unliking all songs.")


@cli.command()
def delete_playlists():
    """Delete all playlists
    """
    logging.info("Retrieving all your playlists...")
    library_playlists = youtube_auth.get_library_playlists(sys.maxsize)
    # Can't delete "Your Likes" playlist
    library_playlists = list(filter(lambda playlist: playlist["playlistId"] != "LM", library_playlists))
    logging.info(f"\tRetrieved {len(library_playlists)} playlists.")
    logging.info("Begin deleting playlists...")
    progress_bar = manager.counter(total=len(library_playlists), desc="Playlists Deleted", unit="playlists")
    for playlist in library_playlists:
        logging.info(f"Processing playlist: {playlist['title']}")
        try:
            response = youtube_auth.delete_playlist(playlist["playlistId"])
            if response:
                logging.info(f"\tRemoved playlist \"{playlist['title']}\" from your library.")
            else:
                logging.error(f"\tFailed to remove playlist \"{playlist['title']}\" from your library.")
        except Exception:
            logging.error(f"\tCould not delete playlist {playlist['title']}. It might be a YT Music curated playlist.")
        progress_bar.update()
    logging.info("Finished deleting all playlists")


@cli.command()
@click.pass_context
def delete_all(ctx):
    """Executes delete-uploads, remove-library, unlike-all, and delete_playlists"""
    ctx.invoke(delete_uploads)
    ctx.invoke(remove_library)
    ctx.invoke(unlike_all)
    ctx.invoke(delete_playlists)
