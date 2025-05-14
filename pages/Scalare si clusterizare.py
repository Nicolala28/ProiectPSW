import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Setări inițiale
st.set_page_config(page_title="Prelucrări Statistice", layout="wide")
st.title("🎵 Clusterizare și scalare")
st.markdown("""
Această aplicație permite scalarea și clusterizarea pieselor muzicale folosind KMeans.
""")

# Încarcă direct fișierul CSV dintr-o cale fixă
csv_path = "data/data_with_encoding.csv"

try:
    df = pd.read_csv(csv_path)
    st.success("Fișierul a fost încărcat cu succes!")
except FileNotFoundError:
    st.error(f"Fișierul '{csv_path}' nu a fost găsit. Verifică dacă calea este corectă.")
    st.stop()




# Coloane numerice pentru clustering
numeric_cols = [
    'bpm', 'key_encoded', 'mode_encoded', 'danceability_%', 'valence_%',
    'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%',
    'in_spotify_playlists', 'in_spotify_charts',
    'in_apple_playlists', 'in_apple_charts',
    'in_deezer_playlists', 'in_deezer_charts',
    'in_shazam_charts', 'genre_freq_encoded', 'country_list_encoded', 'released_month', 'released_year', 'released_day', 'artist_count'
]



# Verifică dacă toate coloanele există
missing_cols = [col for col in numeric_cols if col not in df.columns]
if missing_cols:
    st.error(f"Următoarele coloane lipsesc: {missing_cols}")
    st.stop()

# Selectează coloanele numerice
X = df[numeric_cols]

# Scalează datele
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Selectează numărul de clustere
n_clusters = st.slider("Selectează numărul de clustere", 2, 10, 4)

# Aplică KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(X_scaled)

# Adaugă rezultatul în DataFrame
df['cluster'] = cluster_labels

# Afișează câteva exemple
st.subheader("🔍 Exemple de înregistrări după clusterizare")
cols_to_show = ['track_name', 'streams', 'cluster']
cols_present = [col for col in cols_to_show if col in df.columns]
for i in range(n_clusters):
    st.markdown(f"### Exemple din Clusterul {i}")
    st.dataframe(df[df['cluster'] == i][cols_present].head(3))

# with st.expander("✅ Coloane numerice disponibile în DataFrame"):
#     numeric_all = df.select_dtypes(include=np.number).columns.tolist()
#     st.write(numeric_all)
#
# with st.expander("📌 Coloane folosite pentru clustering (numeric_cols)"):
#      st.write(numeric_cols)
#
# with st.expander("❗ Coloane numerice care NU au fost incluse în clustering"):
#     missing_from_clustering = list(set(numeric_all) - set(numeric_cols))
#     if missing_from_clustering:
#         st.write(missing_from_clustering)
#     else:
#         st.write("✅ Toate coloanele numerice au fost incluse.")

st.subheader("📌 Caracteristici medii per cluster")
st.dataframe(df.groupby('cluster')[numeric_cols].mean().round(2))

from sklearn.decomposition import PCA

# PCA pentru proiecție 2D
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Exemplu înregistrări
cols_to_show = ['track_name', 'artist_name', 'streams', 'cluster']
cols_present = [col for col in cols_to_show if col in df.columns]

# Vizualizare PCA 2D – dimensiune mai mică
st.subheader("🎯 Vizualizare 2D a clusterelor (PCA)")
fig, ax = plt.subplots(figsize=(7, 3))
cmap = plt.cm.get_cmap('rainbow', n_clusters)

for cluster_id in range(n_clusters):
    mask = cluster_labels == cluster_id
    ax.scatter(
        X_pca[mask, 0],
        X_pca[mask, 1],
        label=f"Cluster {cluster_id}",
        alpha=0.7,
        color=cmap(cluster_id)
    )

ax.set_xlabel("Componenta Principală 1")
ax.set_ylabel("Componenta Principală 2")
ax.set_title("Clusterizare KMeans (proiecție PCA 2D)")
ax.legend(title="Clustere")
st.pyplot(fig)

# Distribuție stream-uri per cluster – tot cu dimensiune mai mică
if 'streams' in df.columns:
    st.subheader("📊 Distribuția stream-urilor în funcție de cluster")
    fig2, ax2 = plt.subplots(figsize=(7, 3))  # <--- Dimensiune mai mică și aici
    sns.boxplot(data=df, x='cluster', y='streams', ax=ax2)
    ax2.set_title("Streams per cluster")
    st.pyplot(fig2)

# # Export
# st.download_button(
#     "📥 Descarcă datele cu clustere",
#     df.to_csv(index=False).encode('utf-8'),
#     "clustered_tracks.csv",
#     "text/csv"
# )