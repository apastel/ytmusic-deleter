from ytmusicapi import YTMusic
import sys

youtube_auth = None
try:
    youtube_auth = YTMusic('headers_auth.json')
except KeyError:
    sys.exit('Cookie invalid. Did you paste your cookie into headers_auth.json?')

while True:
    uploaded_albums = youtube_auth.get_library_upload_albums()
    if not len(uploaded_albums) > 0:
        break
    for album in uploaded_albums:
        try:
            artist = album.get('artists')[0].get('name') if len(album.get('artists')) > 0 else "Unknown Artist"
            title = album.get("title")
            response = youtube_auth.delete_upload_entity(album['browseId'])
            if response == 'STATUS_SUCCEEDED':
                print(f'Deleted {artist} - {title}')
            else:
                print(f'Failed to delete {artist} - {title}')
        except (AttributeError, TypeError):
            pass

print('Finished deleting uploaded albums!')
