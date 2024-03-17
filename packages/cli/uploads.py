import logging
import re

import constants as const
from progress import manager
from progress import update_progress
from ytmusicapi import YTMusic


def maybe_delete_uploaded_albums(ctx, youtube_auth: YTMusic, add_to_library=False):
    """
    Retrieve all of the uploaded songs, then filter the list to just songs from unique albums.
    Iterate over each album-unique song. If `add_to_library` is true, search the YTM online catalog
    using "<artist> <album_title>" and see if there's an album that matches it. If a match is found,
    add the album to the library and delete the entire uploaded album that it's from. If a match wasn't
    found, keep the uploaded album. If `add_to_library` is false, delete the uploaded album that the
    song is from (or just the song if it wasn't part of an album).
    """
    logging.info("Retrieving all uploaded songs...")
    albums_deleted = 0
    uploaded_songs = youtube_auth.get_library_upload_songs(limit=None)
    if not uploaded_songs:
        return (albums_deleted, 0)
    logging.info(f"Retrieved {len(uploaded_songs)} uploaded songs from your library.")

    album_unique_songs = list(
        {
            v["album"]["id"] if v.get("album") else v["entityId"]: v
            for v in uploaded_songs
        }.values()
    )
    progress_bar = manager.counter(
        total=len(album_unique_songs),
        desc="Albums Processed",
        unit="albums",
        enabled=not ctx.obj["STATIC_PROGRESS"],
    )
    for song in album_unique_songs:
        artist = (
            song["artists"][0]["name"]
            if song.get("artists")  # Using `get` ensures key exists and isn't []
            else const.UNKNOWN_ARTIST
        )
        album_title = (
            song["album"]["name"] if song.get("album") else const.UNKNOWN_ALBUM
        )
        logging.info(f"Processing album: {artist} - {album_title}")
        if add_to_library:
            if artist == const.UNKNOWN_ARTIST or album_title == const.UNKNOWN_ALBUM:
                if artist == const.UNKNOWN_ARTIST:
                    logging.warn("\tSong is missing artist metadata.")
                if album_title == const.UNKNOWN_ALBUM:
                    logging.warn("\tSong is missing album metadata.")
                logging.warn("\tSkipping match search and will not delete.")
                update_progress(ctx, progress_bar)
                continue
            elif not add_album_to_library(youtube_auth, artist, album_title):
                logging.warn(
                    f"\tNo album was added to library for '{artist} - {album_title}'. Will not delete from uploads."
                )
                update_progress(ctx, progress_bar)
                continue
        response = youtube_auth.delete_upload_entity(
            song["album"]["id"] if song.get("album") else song["entityId"]
        )
        if response == "STATUS_SUCCEEDED":
            logging.info("\tDeleted album from uploads.")
            albums_deleted += 1
        else:
            logging.error("\tFailed to delete album from uploads")
        update_progress(ctx, progress_bar)
    return (albums_deleted, len(album_unique_songs))


def add_album_to_library(youtube_auth: YTMusic, upload_artist, upload_album_title):
    """
    Search for "<artist> <album title>" in the YTM online catalog.

    `Return`: `True` if an album was added to library, `False` otherwise
    """
    logging.info(
        f"\tSearching for '{upload_artist} - {upload_album_title}' in online catalog..."
    )
    search_results = youtube_auth.search(f"{upload_artist} {upload_album_title}")
    logging.debug(f"There were {len(search_results)} search results.")
    for search_result in search_results:
        # Find the first album for which the artist and album title are substrings
        if search_result["resultType"] == "album" and match_found(
            search_result, upload_artist, upload_album_title
        ):
            catalog_album = youtube_auth.get_album(search_result["browseId"])
            logging.info(
                f"\tFound matching album \"{catalog_album['artists'][0]['name'] if catalog_album.get('tracks') else const.UNKNOWN_ARTIST}"
                f" - {catalog_album['title']}\" in YouTube Music. Adding to library..."
            )
            success = youtube_auth.rate_playlist(
                catalog_album["audioPlaylistId"], const.LIKE
            )
            if success:
                logging.info("\tAdded album to library.")
                return True
            else:
                logging.error("\tFailed to add album to library")
                return False
    logging.info(
        f"No matches were found in YTM for `{upload_artist} - {upload_album_title}`"
    )
    return False


def match_found(search_result, upload_artist, upload_title):
    """
    Do a string comparison to check if the search result matches the album artist
    and title of the upload. Getting the artist of the search result has run into
    problems due to Google changing response objects, so the dict structure may change
    again in the future.

    When doing the comparison, an uploaded album title like "Sabotage" will match
    against "Sabotage (2021 Remaster)" because the string "Sabotage" is still
    `in` "Sabotage (2021 Remaster)". But if the uploaded album is "Sabotage (Expanded Edition)"
    then it won't find any matches among the available YTM albums, so that's why we do an
    additional check where we truncate the parenthetical expressions and just see if
    "Sabotage" has a match against "Sabotage".

    `Returns`: `True` if the `search_result` is a match, `False` otherwise.
    """
    upload_artist = upload_artist.lower()
    upload_title = upload_title.lower()
    try:
        logging.debug("Get search result's artist name.")
        search_result_artist = str(search_result["artist"]).lower()
    except KeyError:
        logging.debug(
            "Encountered KeyError with artist name, now checking artists list"
        )
        logging.debug(search_result)
        search_result_artist = str(
            search_result["artists"][1]["name"] if "artists" in search_result else ""
        ).lower()
    try:
        logging.debug("Get search result album title title")
        search_result_title = str(search_result["title"]).lower()
    except KeyError:
        logging.error(
            "Encountered KeyError getting search result's album title.\
                      Cannot check this search result for a match."
        )
        return False

    logging.debug(f"Your upload is: {upload_artist} - {upload_title}")
    logging.debug(
        f"The possible match online is {search_result_artist} - {search_result_title}"
    )
    if upload_artist in search_result_artist and upload_title in search_result_title:
        logging.debug("Found a match")
        return True
    else:
        logging.debug(
            "These are not a match, strip parenthentical expressions and quotes in the album title and try again"
        )
        # Try again but strip out parenthetical expressions at the end of the title, and quotes
        regex = r"\s*\([^)]*\)$|\s*\[[^)]*\]$|\"|\'"
        search_result_title = re.sub(regex, "", search_result_title).strip()
        upload_title = re.sub(regex, "", upload_title).strip()
        logging.debug("Now after stripping...")
        logging.debug(f"Your upload is: {upload_artist} - {upload_title}")
        logging.debug(
            f"The possible match online is {search_result_artist} - {search_result_title}"
        )
        match = (
            upload_artist in search_result_artist
            and upload_title in search_result_title
        )
        logging.debug(f"After stripping, this {'is' if match else 'is not'} a match")
        return match
