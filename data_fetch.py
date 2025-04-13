import pandas as pd
import requests
import time
from tqdm import tqdm

'''
# Încărcarea datelor
file_path = "data/spotify-2023.csv"
df = pd.read_csv(file_path, encoding="ISO-8859-1") #encoding pt a evita probleme cu caractere speciale

# Configurare API Spotify
CLIENT_ID = "76d61408203b468e9a1b781c6226ccdb"
CLIENT_SECRET = "86a44efa5bfa4f5784e49b17dff1b3be"

# Obținerea tokenului de acces
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Căutare artist în API Spotify
def get_artist_info(artist_name, token):
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get("artists"):
        items = data["artists"]["items"]
        if len(items) > 0:
            artist = items[0]
            return artist.get("genres", []), artist.get("country", "Unknown")
    return [], "Unknown"

# Adăugarea genului și țării
token = get_spotify_token()
genres_list = []
countries_list = []

for artist in tqdm(df["artist(s)_name"].unique()):
    genres, country = get_artist_info(artist, token)
    genres_list.append(", ".join(genres) if genres else "Unknown")
    countries_list.append(country)
    time.sleep(0.5)  # Evităm rate limiting

# Crearea unui dicționar pentru mapare
artist_info = dict(zip(df["artist(s)_name"].unique(), zip(genres_list, countries_list)))
df["genre"] = df["artist(s)_name"].map(lambda x: artist_info[x][0])
df["country"] = df["artist(s)_name"].map(lambda x: artist_info[x][1])

# Salvarea noului fișier
df.to_csv("data/spotify-2023-enriched.csv", index=False)


print("Fișierul actualizat a fost salvat!")
'''
df = pd.read_csv("data/spotify-2023-enriched.csv", encoding="ISO-8859-1")
df = df.drop(columns=['country'])
df.to_csv("data/spotify-2023-updated.csv", index=False)

print("Ultima coloană 'country' a fost ștearsă și fișierul a fost salvat!")

# df = pd.read_csv("data/data_cleaned_spotify.csv", encoding="ISO-8859-1")
#
# # === 1. Artiști solo (fără colaborări) ===
# solo_df = df[df['artist_count'] == 1].copy()
# solo_artists = solo_df['artist(s)_name'].str.strip()
# solo_freq = solo_artists.value_counts()
#
# # === 2. Artiști din colaborări ===
# multi_artist_df = df[df['artist_count'] > 1].copy()
# multi_artist_df['artist_list'] = multi_artist_df['artist(s)_name'].str.split(',')
# all_collab_artists = [artist.strip() for sublist in multi_artist_df['artist_list'] for artist in sublist]
# collab_freq = pd.Series(all_collab_artists).value_counts()
#
# # === 3. Combinăm frecvențele ===
# combined_freq = solo_freq.add(collab_freq, fill_value=0).astype(int)
#
# # === 4. Creăm DataFrame final cu numele și frecvența ===
# artist_freq_df = pd.DataFrame({
#     'artist_name': combined_freq.index,
#     'artist_total_count': combined_freq.values
# })
#
# # === 5. Salvăm rezultatul într-un CSV ===
# artist_freq_df.to_csv("data/artists_data.csv", index=False)
#
# print("Fișierul complet cu frecvența tuturor artiștilor (solo + colaborări) a fost salvat.")

