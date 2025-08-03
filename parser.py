

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import timedelta, time, datetime
import logging

log_formatter = logging.Formatter('%(message)s')
logger = logging.getLogger('spotify_data')
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

log_file_path = os.path.join(os.getcwd(), 'result.txt')
file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    # SPOTIPY_CLIENT_ID='', 
    # SPOTIPY_CLIENT_SECRET='',
    # SPOTIPY_REDIRECT_URI=''
    ))

def parse_release_date(date_str):
    if len(date_str) == 4:
        return datetime.strptime(date_str, "%Y").date()
    elif len(date_str) == 7:
        return datetime.strptime(date_str, "%Y-%m").date()
    elif len(date_str) == 10:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        return None

def ms_to_time(ms):
    seconds = int(ms / 1000)
    return (datetime.min + timedelta(seconds=seconds)).time()

def show_artist_main_information(artist):
    results = sp.artist(artist['id'])
    artist = {
        'name': results['name'],
        'type': results['type'],
        'genres': results['genres'],
        'url': f"https://open.spotify.com/artist/{results['id']}",
        'id': results['id'],
        'profile_img': results['images'][0]['url'],
        'followers': results['followers']['total']
    }
    return artist

def show_artist_albums_with_tracks(artist):
    albums = []
    album_types = ['single', 'album']

    for album_type in album_types:
        results = sp.artist_albums(artist['id'], album_type=album_type)
        albums.extend(results['items'])

        while results['next']:
            results = sp.next(results)
            albums.extend(results['items'])

    albums.sort(key=lambda album: album['name'].lower())
    processed_titles = set()
    albums_data = []

    for album in albums:
        title = album['name']
        if title in processed_titles:
            continue
        processed_titles.add(title)

        total_duration = 0

        album_info = {
            'title': title,
            'album_type': album['album_type'],
            'total_tracks': album['total_tracks'],
            'release_date': parse_release_date(album['release_date']),
            'url': album['external_urls']['spotify'],
            'id': album['id'],
            'tracks': []
        }
        
        logger.info(f"\nАЛЬБОМ: {album_info['title']} ({album_info['album_type']}, {album_info['release_date']})")
        logger.info(f"Ссылка: {album_info['url']}")
        logger.info(f"Треков: {album_info['total_tracks']}")

        tracks_result = sp.album_tracks(album['id'])
        tracks = tracks_result['items']

        while tracks_result['next']:
            tracks_result = sp.next(tracks_result)
            tracks.extend(tracks_result['items'])

        for track in tracks:
            track_info = {
                'title': track['name'],
                'type': track['type'],
                'track_number': track['track_number'],
                'disc_number': track['disc_number'],
                'duration': ms_to_time(track['duration_ms']),
                'explicit': track['explicit'],
                'url': track['external_urls']['spotify'],
                'id': track['id'],
            }

            total_duration += track['duration_ms']

            logger.info(f"\n  ТРЕК: {track_info['title']}")
            logger.info(f"    Тип: {track_info['type']}")
            logger.info(f"    № трека: {track_info['track_number']}")
            logger.info(f"    № диска: {track_info['disc_number']}")
            logger.info(f"    Длительность: {track_info['duration']}")
            logger.info(f"    Explicit: {track_info['explicit']}")
            logger.info(f"    Ссылка: {track_info['url']}")
            album_info['tracks'].append(track_info)

        album_info['total_duration'] = total_duration
        logger.info(f"\nОбщая продолжительность треков в альбоме: {ms_to_time(album_info['total_duration'])}")
        logger.info('---')
        albums_data.append(album_info)

    return albums_data


def normalize_name(name):
    return name.lower().replace('.', '').replace(' ', '')


def start_parsing(artist_name='Eminem'):
    results = sp.search(q='artist:' + artist_name, type='artist', limit=50)
    for item in results['artists']['items']:
        if normalize_name(item['name']) == normalize_name(artist_name):
            artist = item
            artist_dict = show_artist_main_information(artist)
            artist_dict['albums_data'] = show_artist_albums_with_tracks(artist)
            return artist_dict
    return None

start_parsing()