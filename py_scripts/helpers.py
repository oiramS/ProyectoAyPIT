# programa que contiene funciones y bibliotecas

# Autenticación para Spotify
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from spotipy.oauth2 import SpotifyClientCredentials

import spotipy  # Para obtener la fecha de lanzamiento
import lyricsgenius as genius
import pandas as pd
import string

from sklearn.feature_extraction.text import CountVectorizer

from dotenv import dotenv_values

config = dotenv_values(".env")



from spotipy.oauth2 import SpotifyClientCredentials  # Autenticación para Spotify
# Datos para usar el API de Spotify
client_id = config["SPOTIFY_CLIENT_ID"]
client_secret = config["SPOTIFY_CLIENT_SECRET"]
client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
# Objeto para entrar al API
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Para obtener los datos de Genius acerca de las canciones
# Para obtener los datos de Genius acerca de las canciones
def search_data(query, n, access_token):

    # Se agrega retraso, timeout y reintentos en la consulta de datos, para prevenir fallas de obtención de información
    api = genius.Genius(access_token=access_token,
                        sleep_time=0.01, timeout=15, retries=3, verbose=True)

    list_lyrics = []
    list_title = []
    list_artist = []
    list_album = []
    list_year = []

    # Genius, se obtienen canciones del artista por popularidad
    artist = api.search_artist(query, max_songs=n, sort='popularity')
    songs = artist.songs  # Son las canciones
    print(songs)
    print(songs[0].stats)
    for song in songs:
        result = sp.search(q="artist:" + song.artist + " track:" +
                           song.title, type="track", limit="1")  # Consulta a Spotipy
        # print("#################################### SONG " + song.title + " ######################################")
        # print(result['tracks']['items'])
        if (result['tracks']['items'] == []):
            list_year.append('1950')  # Los que no tienen fecha, se van a 1950
        else:
            # Añade la fecha del primer resultado
            release_date = result['tracks']['items'][0]['album']['release_date'][:4]
            list_year.append(release_date)

        list_lyrics.append(song.lyrics)
        list_title.append(song.title)
        list_artist.append(song.artist)

    df = pd.DataFrame({'artist': list_artist, 'title': list_title,
                       'date': list_year, 'lyric': list_lyrics})

    return df

#  Esta función limpia las palabras sin importancia y corrige el formato de las letras de las columnas del marco de datos


def clean_lyrics(df, column):

    df = df
    df[column] = df[column].str.lower()
    df[column] = df[column].str.replace(
        r"verse |[1|2|3]|chorus|bridge|outro", "").str.replace("[", "").str.replace("]", "")
    df[column] = df[column].str.lower().str.replace(
        r"instrumental|intro|guitar|solo|contributor|embed|contributors", "")
    df[column] = df[column].str.replace("\n", " ").str.replace(
        r"[^\w\d'\s]+", "").str.replace("efil ym fo flah", "")
    df[column] = df[column].str.strip()

    return df


# Esta función divide las letras en palabras, remueve stopwords en inglés y crea el lema de cada palabra
def lyrics_to_words(document):

    stop_words = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()
    stopwordremoval = " ".join(
        [i for i in document.lower().split() if i not in stop_words])
    punctuationremoval = ''.join(
        ch for ch in stopwordremoval if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word)
                          for word in punctuationremoval.split())
    return normalized


# Esta función crea una nueva columna llamada décadas que se utiliza para agrupar las canciones y las letras por década según la fecha de lanzamiento para cada canción
def create_decades(df):
    decades = []
    df['date'].fillna(0)
    df['date'] = df['date'].astype("int")

    for year in df['date']:
        if 1950 <= year < 1960:
            decades.append("50s")
        if 1960 <= year < 1970:
            decades.append("60s")
        if 1970 <= year < 1980:
            decades.append("70s")
        if 1980 <= year < 1990:
            decades.append("80s")
        if 1990 <= year < 2000:
            decades.append("90s")
        if 2000 <= year < 2010:
            decades.append("00s")
        if 2010 <= year:
            decades.append("10s")
    df['decade'] = decades
    df = df[['artist', 'title', 'decade', 'date', 'lyric']]

    return df
