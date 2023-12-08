import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
import qrcode
import keys

def process_spotify_playlist_qrcodes(playlist_id):
    # STEP 1: Get links from a Spotify Playlist
    client_id = keys.client_id
    client_secret = keys.client_secret
    redirect_uri = 'http://localhost:7000/callback'
    scope = "playlist-read-private"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                   client_secret=client_secret,
                                                   redirect_uri=redirect_uri,
                                                   scope=scope))
    
    results = sp.playlist_tracks(playlist_id)

    spotify_urls = []
    song_names = []
    track_ids = []
    artist_names = []
    album_names = []
    release_years = []

    for item in results['items']:
        track = item['track']
        spotify_urls.append(track['external_urls']['spotify'])
        song_names.append(track['name'])
        track_ids.append(track['id'])

        artists = ', '.join([artist['name'] for artist in track['artists']])
        artist_names.append(artists)

        album_names.append(track['album']['name'])
        release_years.append(track['album']['release_date'][:4] if 'release_date' in track['album'] else 'Year not available')

    # STEP 2: Look for the Videos on YouTube that correspond to the Spotify list
    youtube = build('youtube', 'v3', developerKey=keys.developerKey)

    youtube_urls = []
    for song, artist, album, year, track_id in zip(song_names, artist_names, album_names, release_years, track_ids):
        query = f"{song} {artist} {album} {year} official music video"
        search_response = youtube.search().list(
            q=query,
            part='id',
            type='video',
            maxResults=1
        ).execute()

        if 'items' in search_response and len(search_response['items']) > 0:
            video_id = search_response['items'][0]['id']['videoId']
            youtube_url = f'https://www.youtube.com/watch?v={video_id}'
            youtube_urls.append(youtube_url)
        else:
            if track_id != 'Track ID not available':
                search_response = youtube.search().list(
                    q=track_id,
                    part='id',
                    type='video',
                    maxResults=1
                ).execute()

                if 'items' in search_response and len(search_response['items']) > 0:
                    video_id = search_response['items'][0]['id']['videoId']
                    youtube_url = f'https://www.youtube.com/watch?v={video_id}'
                    youtube_urls.append(youtube_url)
                else:
                    youtube_urls.append('No YouTube link found')
            else:
                youtube_urls.append('No YouTube link found')

    # STEP 3: Create QR codes for each YouTube video
    def generate_qr_code(url, file_name):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_name)

    for index, url in enumerate(youtube_urls[:5], start=20):
        file_name = f'qr_code_{index}.png'
        generate_qr_code(url, file_name)
        print(f"QR code generated for {url} as {file_name}")

    return spotify_urls, youtube_urls

# Usage:
playlist_id = '48QrrRpwM4k4IGFtJw3tyF'  # Replace with your playlist ID
spotify_links, youtube_links = process_spotify_playlist_qrcodes(playlist_id)

