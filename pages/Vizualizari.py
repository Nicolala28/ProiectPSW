import streamlit as st
import pandas as pd
import plotly.express as px
import io


st.set_page_config(page_title="Vizualizari", layout="wide")

# Stil personalizat
st.markdown(
    """
    <style>
    .custom-title {
       color: #1DB954 !important;
       font-size: 40px;
       text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 class="custom-title">Vizualiari folosind Streamlit</h1>', unsafe_allow_html=True)

# Încarcă datele
df = pd.read_csv("data/spotify-2023-updated.csv", encoding="ISO-8859-1")

# --- SECTIUNEA 1: Vizualizari GENERALE (tip portret, cu coloane) ---
st.subheader("Vizualizări generale")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Evoluția stream-urilor după an")
    df_sel = df.iloc[:45]
    st.line_chart(df_sel.set_index('released_year')['streams'], use_container_width=True)

with col2:
    st.markdown("#### Distribuția după tonalitate (key)")
    fig = px.pie(df_sel, names='key', title='Distribuția pe tonalitate')
    fig.update_layout(
        width=700,  # lățimea în pixeli
        height=500  # înălțimea în pixeli
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
        #### Evoluția stream-urilor după an
        Acest grafic prezintă **evoluția numărului de stream-uri** pentru top 45 piese Spotify din 2023, distribuite pe anii de lansare.
        Fiecare punct reprezintă numărul total de stream-uri obținute într-un an specific, ceea ce ne ajută să observăm cum au evoluat tendințele de ascultare pe Spotify în timp.
        """)

    st.markdown("""
       #### Distribuția pe tonalitate (key)
       Graficul de mai sus prezintă distribuția pieselor după **tonalitatea (key)** lor. Fiecare sector reprezintă câte o tonalitate și ponderea pieselor care au fost lansate în acea tonalitate.
       Tonalitatea sau „key-ul” unei piese poate influența cum percepem melodia, dar și stilul acesteia (ex: major, minor etc.).
       """)

st.markdown("---")

# --- SECTIUNEA 2: Tabele & JSON ---
st.subheader("Informații Tabelare și JSON")

col3, col4 = st.columns([2, 1])  # coloana 3 mai mare pt tabel

with col3:
    st.markdown("#### Primele înregistrări")
    df_selected = df[['track_name', 'artist(s)_name', 'released_year']]
    df_selected_rows = df_selected.iloc[:8]
    st.dataframe(df_selected_rows, use_container_width=True)

with col4:
    st.markdown("#### Format JSON")
    df_json = df_selected_rows.to_json(orient='records')
    st.json(df_json)

st.markdown("---")


st.markdown("""
### 📋 Dicționar de variabile

| Variabilă                  | Tip        | Descriere                                                                                 | Utilitate model          |
|----------------------------|------------|-------------------------------------------------------------------------------------------|---------------------------|
| `track_name`              | object     | Numele piesei                                                                            | ❌ Doar pentru afișare    |
| `artist(s)_name`          | object     | Numele artistului/artiștilor                                                             | 🔸 Poate fi folosit cu encoding (TF-IDF/Frequency) |
| `artist_count`            | int64      | Număr de artiști implicați pe piesă                                                      | ✅ Variabilă numerică relevantă |
| `released_year`           | int64      | Anul lansării                                                                            | ✅ Temporală              |
| `released_month`          | int64      | Luna lansării                                                                            | ✅ Temporală              |
| `released_day`            | int64      | Ziua lansării                                                                            | 🔸 Mai puțin relevantă    |
| `in_spotify_playlists`    | int64      | Nr. de playlist-uri Spotify în care apare piesa                                          | ✅ Predictivă             |
| `in_spotify_charts`       | int64      | Nr. de apariții în topuri Spotify                                                        | ✅ Predictivă             |
| `in_apple_playlists`      | int64      | Nr. de playlist-uri Apple Music                                                          | ✅ Predictivă             |
| `in_apple_charts`         | int64      | Nr. de apariții în topuri Apple Music                                                    | ✅ Predictivă             |
| `in_deezer_playlists`     | int64*     | Nr. de playlist-uri Deezer *(necesită conversie din string)*                            | ✅ Predictivă             |
| `in_deezer_charts`        | int64      | Nr. de apariții în topuri Deezer                                                         | ✅ Predictivă             |
| `in_shazam_charts`        | int64*     | Nr. de apariții în topuri Shazam *(valori lipsă + conversie)*                           | ✅ Predictivă             |
| `streams`                 | int64*     | Nr. total de stream-uri *(valoare-țintă, trebuie convertită din string)*                | 🎯 Variabilă țintă        |
| `bpm`                     | int64      | Tempo-ul piesei (bătăi pe minut)                                                         | ✅ Audio numerică         |
| `key`                     | object     | Tonalitatea piesei (Do, Re, etc.)                                                        | 🔸 Codificare necesară    |
| `mode`                    | object     | Mod muzical (major/minor)                                                                | 🔸 Codificare necesară    |
| `danceability_%`          | int64      | Gradul de dansabilitate                                                                  | ✅ Audio numerică         |
| `valence_%`               | int64      | Emoționalitate pozitivă                                                                  | ✅ Audio numerică         |
| `energy_%`                | int64      | Energie                                                                                  | ✅ Audio numerică         |
| `acousticness_%`          | int64      | Cât de acustică este piesa                                                               | ✅ Audio numerică         |
| `instrumentalness_%`      | int64      | Gradul de instrumentalizare                                                              | ✅ Audio numerică         |
| `liveness_%`              | int64      | Probabilitatea ca piesa să fie live                                                      | ✅ Audio numerică         |
| `speechiness_%`           | int64      | Cât de mult conține vorbire (spoken words)                                               | ✅ Audio numerică         |
| `genre`                   | object     | Genul muzical                                                                            | 🔸 Codificare necesară    |
""", unsafe_allow_html=True)

def convert_numeric_columns(df):
    df['streams'] = df['streams'].astype(str).str.replace(',', '').astype(float)
    df['in_deezer_playlists'] = df['in_deezer_playlists'].astype(str).str.replace(',', '').astype(int)
    df['in_shazam_charts'] = pd.to_numeric(df['in_shazam_charts'], errors='coerce')
    return df

df = convert_numeric_columns(df)


st.markdown("""
Am efectuat conversia `object` -> `int` pentru următoarele variabile:

- `streams`
- `in_deezer_playlists`
- `in_shazam_charts`
""")

### 📋 Dicționar de variabile
st.subheader("📊 Statistici descriptive pentru variabilele numerice")
st.dataframe(df.describe(), use_container_width=True)


def afiseaza_info_df(df):
    # Creăm un buffer pentru a capta ieșirea din df.info()
    buffer = io.StringIO()

    # Apelăm df.info() și direcționăm rezultatul în buffer
    df.info(buf=buffer)

    # Obținem valoarea din buffer (informațiile despre DataFrame)
    info_str = buffer.getvalue()

    # Afișăm informațiile în Streamlit
    st.text("ℹ️ Info despre DataFrame:")
    st.text(info_str)