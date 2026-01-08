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
3. Введите свои SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET:
    ```bash
    parser = SpotifyApiAlbumsSongsParser(SPOTIPY_CLIENT_ID="",
                                     SPOTIPY_CLIENT_SECRET="",
                                     is_create_results_file=True)
## Использование
Используя метод start_parsing() добавьте исполнителей для поиска в список. Поддерживается поиск как по имени, так и по URL, однако я советую использовать вариант с URL, поскольку поиск по имени может давать сбои, выдавая не тех исполнителей. Примеры возможных форматов входных данных указаны в примере ниже:
# Пример используемый в parser.py:
    parser.start_parsing(["Eminem",
                      "https://open.spotify.com/artist/1ZwdS5xdxEREPySFridCfh?si=f676518dca104d48", 
                      "https://open.spotify.com/artist/6DPYiyq5kWVQS4RGwxzPC7"])


