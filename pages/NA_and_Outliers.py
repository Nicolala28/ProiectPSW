import streamlit as st
import pandas as pd
import plotly.express as px
import io

st.title("Tratarea valorilor lipsă și a outlierilor")

df = pd.read_csv("data/spotify-2023-updated.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.strip()

# Folosim st.write pentru a afișa df.info()
st.write("Info despre DataFrame:")
buffer = io.StringIO()
df.info(buf=buffer)
info_str = buffer.getvalue()
st.text("ℹ️ Info despre DataFrame:")
st.text(info_str)

# Codul tău cu tratarea NA + outlieri
st.subheader("Tratarea valorilor lipsă")

df_clean=df.copy()

# Afișează numărul de valori lipsă înainte de completare
missing_before = df_clean[['key', 'in_shazam_charts']].isnull().sum().reset_index()
missing_before.columns = ['Coloana', 'Valori lipsă înainte']
st.table(missing_before)

# Tratare 'key' (categoric): completare cu moda
if df_clean['key'].isnull().sum() > 0:
    df_clean['key'] = df_clean['key'].fillna(df_clean['key'].mode()[0])

# Tratare 'in_shazam_charts' (numerică, dar poate fi object): conversie + completare
df_clean['in_shazam_charts'] = pd.to_numeric(df_clean['in_shazam_charts'], errors='coerce')
if df_clean['in_shazam_charts'].isnull().sum() > 0:
    df_clean['in_shazam_charts'] = df_clean['in_shazam_charts'].fillna(df_clean['in_shazam_charts'].median())

# Afișează numărul de valori lipsă după completare
missing_after = df_clean[['key', 'in_shazam_charts']].isnull().sum().reset_index()
missing_after.columns = ['Coloana', 'Valori lipsă după']
st.table(missing_after)

# --- SECTIUNEA 4: Valori extreme (outlieri) ---
st.subheader(" Valori extreme (Outlieri)")

st.markdown("""
Outlierii sunt valori care se abat puternic de la restul datelor. Pot fi erori de introducere, dar uneori sunt pur și simplu excepții (ex: piese virale, artiști extrem de populari etc.). 
Mai jos folosim metoda IQR pentru a identifica valorile extreme.
""")

def find_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)  # Calculăm Q1
    Q3 = df[col].quantile(0.75)  # Calculăm Q3
    IQR = Q3 - Q1  # Intervalul intercuartilic
    lower_bound = max(Q1 - 1.5 * IQR, 0) # Limita inferioară
    upper_bound = max(Q3 + 1.5 * IQR, 0) # Limita superioară
    outliers_df = df[(df[col] < lower_bound) | (df[col] > upper_bound)]  # Selectăm outlierii
    return lower_bound, upper_bound, outliers_df

# Coloane relevante pe care le-ai menționat
relevant_cols = [
    'track_name', 'artist(s)_name', 'artist_count', 'released_year', 'released_month', 'released_day',
    'in_spotify_playlists', 'in_spotify_charts', 'streams', 'in_apple_playlists', 'in_apple_charts',
    'in_deezer_playlists', 'in_deezer_charts', 'in_shazam_charts', 'bpm', 'key', 'mode',
    'danceability_%', 'valence_%', 'energy_%', 'acousticness_%', 'instrumentalness_%',
    'liveness_%', 'speechiness_%', 'genre'
]

# Filtrăm doar coloanele numerice
numeric_cols = df_clean.select_dtypes(include='number').columns.tolist()

# Comparăm lista de coloane numerice cu cele relevante și le păstrăm doar pe cele care sunt numerice
relevant_numeric_cols = [col for col in relevant_cols if col in numeric_cols]

# Calculăm outlieri pentru fiecare coloană relevantă
for col in relevant_numeric_cols:
    if col in df_clean.columns:
        st.markdown(f"###  Coloana: `{col}`")

        # Detectare outlieri
        lower, upper, outliers = find_outliers_iqr(df_clean, col)
        st.write(f"🔹 Limita inferioară: `{lower:,.0f}`")
        st.write(f"🔹 Limita superioară: `{upper:,.0f}`")
        st.write(f"🔹 Număr de outlieri: `{len(outliers)}` din `{len(df_clean)}`")

        # Boxplot interactiv cu Plotly
        fig_box = px.box(df_clean, y=col, title="Boxplot pentru {col} (cu outlieri)")
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("---")
