
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import timedelta, datetime
import logging
import re

class SpotifyApiAlbumsSongsParser:

    def __init__(self, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, is_create_results_file):
        self.SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
        self.SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET

        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.SPOTIPY_CLIENT_ID, 
            client_secret=self.SPOTIPY_CLIENT_SECRET,
            ))
        
        log_formatter = logging.Formatter('%(message)s')
        self.logger = logging.getLogger('spotify_data')
        self.logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self.logger.addHandler(console_handler)

        if is_create_results_file:
            log_file_path = os.path.join(os.getcwd(), 'result.txt')
            file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
            file_handler.setFormatter(log_formatter)
            self.logger.addHandler(file_handler)


    def parse_release_date(self, date_str):
        if len(date_str) == 4:
            return datetime.strptime(date_str, "%Y").date()
        elif len(date_str) == 7:
            return datetime.strptime(date_str, "%Y-%m").date()
        elif len(date_str) == 10:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            return None

    def ms_to_time(self, ms):
        seconds = int(ms / 1000)
        return (datetime.min + timedelta(seconds=seconds)).time()

    def show_artist_main_information(self, artist_id_or_url):
        results = self.sp.artist(artist_id_or_url)
        
        artist_info = {
            'name': results['name'],
            'type': results['type'],
            'genres': results['genres'],
            'url': f"https://open.spotify.com/artist/{results['id']}",
            'id': results['id'],
            'profile_img': results['images'][0]['url'] if results['images'] else None,
            'followers': results['followers']['total']
        }
        
        self.logger.info(f"\nИМЯ ИСПОЛНИТЕЛЯ: {artist_info['name']}")
        self.logger.info(f"ССЫЛКА НА ИЗОБРАЖЕНИЕ ПРОФИЛЯ ИСПОЛНИТЕЛЯ: {artist_info['profile_img']}")
        self.logger.info(f"ССЫЛКА: {artist_info['url']}")
        self.logger.info(f"ЖАНРЫ: {artist_info['genres']}")
        self.logger.info(f"КОЛИЧЕСТВО ПОДПИСЧИКОВ: {artist_info['followers']} \n --- \n")
        
        return artist_info
    

    def show_artist_albums_with_tracks(self, artist):
        albums = []
        album_types = ['single', 'album']

        for album_type in album_types:
            results = self.sp.artist_albums(artist['id'], album_type=album_type)
            albums.extend(results['items'])

            while results['next']:
                results = self.sp.next(results)
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
                'release_date': self.parse_release_date(album['release_date']),
                'url': album['external_urls']['spotify'],
                'id': album['id'],
                'tracks': []
            }
            
            self.logger.info(f"\nАЛЬБОМ: {album_info['title']} ({album_info['album_type']}, {album_info['release_date']})")
            self.logger.info(f"Ссылка: {album_info['url']}")
            self.logger.info(f"Треков: {album_info['total_tracks']}")

            tracks_result = self.sp.album_tracks(album['id'])
            tracks = tracks_result['items']

            while tracks_result['next']:
                tracks_result = self.sp.next(tracks_result)
                tracks.extend(tracks_result['items'])

            for track in tracks:
                track_info = {
                    'title': track['name'],
                    'type': track['type'],
                    'track_number': track['track_number'],
                    'disc_number': track['disc_number'],
                    'duration': self.ms_to_time(track['duration_ms']),
                    'explicit': track['explicit'],
                    'url': track['external_urls']['spotify'],
                    'id': track['id'],
                }

                total_duration += track['duration_ms']

                self.logger.info(f"\n  ТРЕК: {track_info['title']}")
                self.logger.info(f"    Тип: {track_info['type']}")
                self.logger.info(f"    № трека: {track_info['track_number']}")
                self.logger.info(f"    № диска: {track_info['disc_number']}")
                self.logger.info(f"    Длительность: {track_info['duration']}")
                self.logger.info(f"    Explicit: {track_info['explicit']}")
                self.logger.info(f"    Ссылка: {track_info['url']}")
                album_info['tracks'].append(track_info)

            album_info['total_duration'] = total_duration
            self.logger.info(f"\nОбщая продолжительность треков в альбоме: {self.ms_to_time(album_info['total_duration'])}")
            self.logger.info('---')
            albums_data.append(album_info)

        return albums_data


    def normalize_name(self, name):
        return re.sub(r"[-_.]+", "-", name).lower()
    
    def search_for_artist(self, artist):
        
        if isinstance(artist, str) and ("spotify.com/artist/" in artist):
            try:
                artist_info = self.show_artist_main_information(artist)
                artist_info['albums_data'] = self.show_artist_albums_with_tracks({'id': artist_info['id']})
                return artist_info
            except Exception as e:
                self.logger.error(f"Ошибка при получении артиста: {e}")
                return None
        
        elif isinstance(artist, str):
            results = self.sp.search(q='artist:' + artist, type='artist', limit=50)
            
            target_name = self.normalize_name(artist)
            
            for item in results['artists']['items']:
                if self.normalize_name(item['name']) == target_name:
                    artist_info = self.show_artist_main_information(item['id'])
                    artist_info['albums_data'] = self.show_artist_albums_with_tracks({'id': item['id']})
                    return artist_info
            
            self.logger.warning(f"Артист '{artist}' не найден")
            return None
        
        else:
            self.logger.error(f"Неизвестный формат входных данных: {type(artist)}")
            return None


    def start_parsing(self, artists: list):
        data = []
        for artist in artists:
            artist_data = self.search_for_artist(artist)
            data.append(artist_data)
        return data

parser = SpotifyApiAlbumsSongsParser(SPOTIPY_CLIENT_ID="",
                                     SPOTIPY_CLIENT_SECRET="",
                                     is_create_results_file=True)

result = parser.start_parsing(["Eminem",
                  "https://open.spotify.com/artist/1ZwdS5xdxEREPySFridCfh?si=f676518dca104d48", 
                  "https://open.spotify.com/artist/6DPYiyq5kWVQS4RGwxzPC7"])
