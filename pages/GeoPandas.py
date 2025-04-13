import pandas as pd
import geopandas as gpd
import streamlit as st
import chardet
import matplotlib.pyplot as plt
from shapely.geometry import Point
from geopy.distance import geodesic
import numpy as np
import folium

st.set_page_config(page_title="Geopandas", layout="wide")
st.title("Analiza geografica a distribuitiei melodiilor si artistilor")

# Încarcă datele din fișierele CSV
df = pd.read_csv("data/data_cleaned_spotify.csv", encoding="utf-8")
artist_data = pd.read_csv("data/artists_data.csv", index_col=None)  # Fișierul cu informații despre artiști

# Curăță coloanele pentru a elimina spațiile suplimentare
df.columns = df.columns.str.strip()
artist_data.columns = artist_data.columns.str.strip()

# Înlocuim NaN cu 'Unknown' și convertim toate valorile în tipul 'str'
artist_data['country'] = artist_data['country'].fillna('Unknown').astype(str)

# Creăm un dictionar cu țările fiecărui artist
artist_country_mapping = artist_data.set_index('artist_name')['country'].to_dict()

def get_country_list(artist_names):
    # Separați artiștii pe baza virgulei
    artist_names_list = artist_names.split(', ')
    # Căutăm țara fiecărui artist și le adăugăm într-o listă
    country_list = {artist_country_mapping.get(artist, 'Unknown') for artist in artist_names_list}
    # Returnăm lista de țări unică (fără duplicate)
    return ', '.join(sorted(country_list))

# Aplicăm funcția pentru a adăuga o nouă coloană 'country_list'
df['country_list'] = df['artist(s)_name'].apply(get_country_list)

# --- Salvăm fișierul cu noile informații ---
df.to_csv("data/data_with_country_list.csv", index=False)

print("Fișierul cu lista de țări a fost salvat.")

# Încărcăm datele țărilor
countries = gpd.read_file("data/geopandas_data/ne_110m_admin_0_countries.shp")

# Creăm un dicționar pentru a stoca coordonatele (centroid) pentru fiecare țară
country_coordinates = {}
for _, row in countries.iterrows():
    country_name = row['ADMIN']
    # Extragem centrul țării ca punct (centroid)
    country_centroid = row.geometry.centroid
    # Salvăm coordonatele latitudine și longitudine
    country_coordinates[country_name] = (country_centroid.y, country_centroid.x)

# Adăugăm un mapping pentru corectarea denumirilor
country_mapping = {
    "United States": "United States of America",
    "Columbia": "Colombia",
    # Verifică dacă denumirea este corectă
    # Adaugă alte mappinguri dacă este necesar
}

# Modifică funcția get_coordinates_for_countries pentru a utiliza acest mapping
def get_coordinates_for_countries(country_list):
    countries_list = country_list.split(', ')
    coordinates = []
    for country in countries_list:
        # Folosim mappingul pentru denumirile țării
        country = country_mapping.get(country, country)  # Dacă nu există în mapping, păstrează denumirea originală
        if country in country_coordinates:
            coordinates.append(country_coordinates[country])
        else:
            print(f"Coordonate lipsă pentru: {country}")  # Debugging
            coordinates.append(None)
    return coordinates

# Aplicăm funcția pentru a adăuga coordonatele
df['coordinates'] = df['country_list'].apply(get_coordinates_for_countries)

# --- 1. Vizualizare harta globală cu distribuția melodiilor ---
# Creăm un GeoDataFrame pentru a adăuga punctele artiștilor pe hartă
# Explodăm dataframe-ul ca să avem câte un rând per coordonată
exploded_df = df.explode('coordinates').reset_index(drop=True)

# Eliminăm rândurile cu coordonate lipsă
exploded_df = exploded_df[exploded_df['coordinates'].notnull()].copy()

# Creăm o coloană geometry din coordonate
exploded_df['geometry'] = exploded_df['coordinates'].apply(lambda coord: Point(coord[1], coord[0]))

# Construim GeoDataFrame corect
gdf_artists = gpd.GeoDataFrame(exploded_df, geometry='geometry', crs=countries.crs)

# Plotăm harta cu distribuția melodiilor
fig, ax = plt.subplots(figsize=(10, 10))
countries.plot(ax=ax, color='lightgrey')
gdf_artists.plot(ax=ax, color='red', markersize=5, alpha=0.5)

plt.title("Distribuția melodiilor pe hartă")
st.pyplot(fig)

# --- 2. Vizualizare harta cu granițele și vecinii țărilor ---
# Creăm o hartă care include atât țărilor, cât și vecinii lor
fig, ax = plt.subplots(figsize=(12, 12))

# Harta țărilor
countries.plot(ax=ax, color='lightgrey', edgecolor='black')

# Adăugăm vecinii pentru fiecare țară
for _, row in countries.iterrows():
    country_name = row['ADMIN']
    neighbors = countries[countries.geometry.touches(row.geometry)]
    for _, neighbor_row in neighbors.iterrows():
        ax.plot([row.geometry.centroid.x, neighbor_row.geometry.centroid.x],
                [row.geometry.centroid.y, neighbor_row.geometry.centroid.y], color="blue", alpha=0.3)

gdf_artists.plot(ax=ax, color='red', markersize=5, alpha=0.5)
plt.title("Distribuția melodiilor și vecinii țărilor")
st.pyplot(fig)

# --- 3. Calcularea distanțelor și traseelor între artiști ---
def calculate_distances(coords):
    if len(coords) > 1:
        distances = []
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                if coords[i] and coords[j]:
                    dist = geodesic(coords[i], coords[j]).kilometers
                    distances.append((i, j, dist))
        return distances
    return []

# Calculăm distanțele între țările din fiecare melodie
distances_list = []
for _, row in df.iterrows():
    distances = calculate_distances(row['coordinates'])
    distances_list.extend(distances)

# Creăm un DataFrame pentru distanțele calculate
distances_df = pd.DataFrame(distances_list, columns=["Coord1", "Coord2", "Distance (km)"])

# --- FILTRARE MELODII CU ARTIȘTI DIN SUA ---
df_usa = df[df['country_list'].str.contains("United States of America")]



df_usa['is_collab'] = df_usa['artist(s)_name'].apply(lambda x: ',' in x)

# Explodăm coordonatele pentru fiecare melodie
exploded_usa_df = df_usa.explode('coordinates').reset_index(drop=True)
exploded_usa_df = exploded_usa_df[exploded_usa_df['coordinates'].notnull()].copy()
exploded_usa_df['geometry'] = exploded_usa_df['coordinates'].apply(lambda coord: Point(coord[1], coord[0]))
gdf_usa = gpd.GeoDataFrame(exploded_usa_df, geometry='geometry', crs=countries.crs)

def add_jitter(point, jitter_degree=0.5):
    lat, lon = point.y, point.x
    jittered_lat = lat + np.random.uniform(-jitter_degree, jitter_degree)
    jittered_lon = lon + np.random.uniform(-jitter_degree, jitter_degree)
    return Point(jittered_lon, jittered_lat)

# Aplicăm jitter doar pentru SUA (unde toate punctele sunt identice)
gdf_usa['geometry'] = gdf_usa['geometry'].apply(lambda p: add_jitter(p, jitter_degree=0.7))

# --- ÎNCARCAREA DATELOR CU LACURI ---
lakes = gpd.read_file("data/geopandas_data/ne_110m_admin_0_countries_lakes.shp")  # Înlocuiește cu calea către shapefile-ul lacurilor
if lakes.crs is None:
    lakes.set_crs("EPSG:4326", allow_override=True, inplace=True)

if countries.crs is None:
    countries.set_crs("EPSG:4326", allow_override=True, inplace=True)

lakes = lakes.to_crs(countries.crs)

# --- FILTRARE MELODII CU ARTIȘTI DIN SUA ---
df_usa = df[df['country_list'].str.contains("United States of America")]
df_usa['is_collab'] = df_usa['artist(s)_name'].apply(lambda x: ',' in x)

# Explodăm coordonatele pentru fiecare melodie
exploded_usa_df = df_usa.explode('coordinates').reset_index(drop=True)
exploded_usa_df = exploded_usa_df[exploded_usa_df['coordinates'].notnull()].copy()
exploded_usa_df['geometry'] = exploded_usa_df['coordinates'].apply(lambda coord: Point(coord[1], coord[0]))
gdf_usa = gpd.GeoDataFrame(exploded_usa_df, geometry='geometry', crs=countries.crs)

# Aplicăm jitter doar pentru SUA (pentru a evita suprapunerea punctelor)
def add_jitter(point, jitter_degree=0.5):
    lat, lon = point.y, point.x
    jittered_lat = lat + np.random.uniform(-jitter_degree, jitter_degree)
    jittered_lon = lon + np.random.uniform(-jitter_degree, jitter_degree)
    return Point(jittered_lon, jittered_lat)

gdf_usa['geometry'] = gdf_usa['geometry'].apply(lambda p: add_jitter(p, jitter_degree=0.7))

# --- 2. Plotare hartă cu zoom pe SUA ---
fig, ax = plt.subplots(figsize=(12, 10))

# Fundal: harta lumii
countries.plot(ax=ax, color='lightgrey', edgecolor='white')

# Granițele Statelor Unite evidențiate
usa_geom = countries[countries['ADMIN'] == "United States of America"]
usa_geom.boundary.plot(ax=ax, color='black', linewidth=2)

# Plot lacurile (lacuri mari)
lakes.plot(ax=ax, color='blue', alpha=0.5, label='Lacuri')

# Plot solo (roșu)
gdf_usa[gdf_usa['is_collab'] == False].plot(ax=ax, color='red', markersize=5, label='Solo')

# Plot colaborări (albastru)
gdf_usa[gdf_usa['is_collab'] == True].plot(ax=ax, color='blue', markersize=5, label='Colaborare')

# Setări zoom pe SUA (lat/lon approx)
ax.set_xlim(-130, -60)
ax.set_ylim(20, 55)

# Titlu și legendă
plt.title("Melodii cu artiști din SUA – distribuție cu jitter și lacuri", fontsize=14)
plt.legend()

# Afișează graficul
st.pyplot(fig)


st.dataframe(df_usa)
