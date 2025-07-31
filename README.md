# Spotify API Album & Songs Info Parser

Этот скрипт предназначен для получения информации об альбомах и треках конкретного исполнителя с использованием Spotify Web API через библиотеку Spotipy.

## Возможности

- Поиск нужного исполнителя по точному имени.
- Получение всех `альбомов` и `синглов` исполнителя.
- Сбор полной информации о каждом релизе: название, дата, количество треков, ссылка и т.д.
- Получение всех треков из каждого альбома/сингла.
- Вывод расширенной информации о треках: длительность, номер трека, диск, explicit, URL и т.д.
- Логирование в консоль и сохранение в `result.txt`.

## Установка

1. Клонируйте репозиторий или сохраните файл:
   ```bash
   git clone https://github.com/Gambimoto228/spotify-api-albums-songs-parcer.git
   cd spotify-api-albums-songs-parcer
2. Установите зависимости:
    ```bash
    pip install spotipy
3. Введите свои SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI:
    ```bash
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    SPOTIPY_CLIENT_ID='', 
    SPOTIPY_CLIENT_SECRET='',
    SPOTIPY_REDIRECT_URI=''
    ))
## Использование
`Используется строгое сравнение имен`
    
     artist_name = 'Eminem' #Артист для поиска
    
    results = sp.search(q='artist:' + artist_name, type='artist', limit=50)
    for item in results['artists']['items']:
        if normalize_name(item['name']) == normalize_name(artist_name):
            artist = item
            print(f'Найден артист: {artist['name']}')
            show_artist_albums_with_tracks(artist)