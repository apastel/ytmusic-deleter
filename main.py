from ytmusicapi import YTMusic
import click
import sys


def setup():
    try:
        return YTMusic('headers_auth.json')
    except KeyError:
        sys.exit('Cookie invalid. Did you paste your cookie into headers_auth.json?')

@click.command()
@click.option('--add-to-library', '-l', is_flag=True, help='Add corresponding albums to your library before deleting them from uploads.')
def delete_all_uploaded_albums(add_to_library):
    albums_deleted = 0
    print('Retrieving all uploaded albums...')
    uploaded_albums = youtube_auth.get_library_upload_albums()
    if not uploaded_albums:
        print('No uploaded albums found.')
        return albums_deleted
    print(f'{len(uploaded_albums)} uploaded albums found.')
    for album in uploaded_albums:
        try:
            artist = album.get('artists')[0].get('name') if len(album.get('artists')) > 0 else "Unknown Artist"
            title = album.get("title")
            print(f'{artist} - {title}')
            if add_to_library:
                click.echo('Searching for album in online catalog...')
                album_found = search_for_album(artist, title)
                if not album_found:
                    print('No match for uploaded album found in online catalog. Will not delete.')
                    continue
            response = youtube_auth.delete_upload_entity(album['browseId'])
            if response == 'STATUS_SUCCEEDED':
                print('    Deleted album')
                albums_deleted += 1
            else:
                print('    Failed to delete album')
        except (AttributeError, TypeError) as e:
            print(e)
            continue

    print(f'Deleted {albums_deleted} out of {len(uploaded_albums)} uploaded albums.')
    return albums_deleted

def search_for_album(artist, title):
    search_results = youtube_auth.search(f'{artist} {title}')
    for result in search_results:
        if result['resultType'] == 'album' and str(artist).lower() in str(result['artist']).lower() and str(title).lower() in str(result['title']).lower():
            catalog_album = youtube_auth.get_album(result['browseId'])
            print(f'    Found matching album \"{catalog_album["title"]}\" in YouTube Music. Adding to library...')
            for track in catalog_album['tracks']:
                youtube_auth.rate_song(track['videoId'], 'LIKE')
            print('    Added album to library.')
            return True
    return False

def delete_albumless_songs():
    songs_deleted = 0
    try:
        print('Retriving uploaded songs that are not part of an album.')
        uploaded_songs = youtube_auth.get_library_upload_songs()
    except KeyError:
        return songs_deleted
    if not uploaded_songs:
        return songs_deleted
    
    # Filter for songs that don't have an album, otherwise songs that were skipped in the first batch would get deleted here
    uploaded_songs = [song for song in uploaded_songs if not song['album']]
    
    for song in uploaded_songs:
        try:
            artist = song.get('artist')[0].get('name') if len(song.get('artist')) > 0 else "Unknown Artist"
            title = song.get('title')
            response = youtube_auth.delete_upload_entity(song['entityId'])
            if response == 'STATUS_SUCCEEDED':
                print(f'Deleted {artist} - {title}')
                songs_deleted += 1
            else:
                print(f'Failed to delete {artist} - {title}')
        except (AttributeError, TypeError) as e:
            print(e)
            continue

    print(f'Deleted {songs_deleted} out of {len(uploaded_songs)} uploaded songs that are not part of an album.')
    return songs_deleted


if __name__ == "__main__":
    print('Begin cookie validation...')
    youtube_auth = setup()
    print('Cookie validated.')
    albums_deleted = delete_all_uploaded_albums()
    songs_deleted = delete_albumless_songs()
    print(f'Finished. Deleted {albums_deleted + songs_deleted} total albums.')