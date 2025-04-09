import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Top Spotify Songs 2023", layout="wide")

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
st.markdown('<h1 class="custom-title">Top Spotify Songs 2023</h1>', unsafe_allow_html=True)

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

# --- SECTIUNEA 3: Tratarea valorilor lipsă ---
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

df.columns = df.columns.str.strip()  # Ne asigurăm că nu sunt spații suplimentare în numele coloanelor

# --- SECTIUNEA 6: Aplicarea Frequency Encoding pentru variabila `genre` ---
st.subheader("Aplicarea Frequency Encoding pentru variabila `genre`")

# Verificăm dacă există coloana 'genre' în DataFrame
if 'genre' in df.columns:
    # Calculăm frecvența fiecărui gen
    freq_encoding = df['genre'].value_counts(normalize=True)

    # Aplicăm Frequency Encoding pe coloana `genre`
    df['genre_freq_encoded'] = df['genre'].map(freq_encoding)

    # Afișăm rezultatul
    st.write("DataFrame cu Frequency Encoding aplicat pentru `genre`:")
    st.dataframe(df[['genre', 'genre_freq_encoded']], use_container_width=True)
else:
    st.write("Coloana 'genre' nu există în DataFrame-ul tău.")

# --- SECTIUNEA 7: Aplicarea Label Encoding pentru variabile ordinale ---
st.subheader("Aplicarea Label Encoding pentru variabilele `key` și `mode`")

# Verificăm dacă există coloanele 'key' și 'mode' în DataFrame
if 'key' in df.columns and 'mode' in df.columns:
    # Creăm un obiect de tip LabelEncoder
    le = LabelEncoder()

    # Aplicăm Label Encoding pe coloana `key` și `mode`
    df['key_encoded'] = le.fit_transform(df['key'])
    df['mode_encoded'] = le.fit_transform(df['mode'])

    # Afișăm rezultatul
    st.write("DataFrame cu Label Encoding aplicat pentru `key` și `mode`:")
    st.dataframe(df[['key', 'key_encoded', 'mode', 'mode_encoded']], use_container_width=True)
else:
    st.write("Coloanele 'key' și 'mode' nu există în DataFrame-ul tău.")

# Descriere metodologie
st.markdown("""
Aceste metode de codificare sunt esențiale pentru transformarea datelor categorice într-o formă numerică, care poate fi utilizată de modelele de machine learning.

- **Frequency Encoding** ajută la capturarea relevanței categoriilor în baza frecvenței lor de apariție.
- **Label Encoding** păstrează relațiile ordinale între variabilele care au o ierarhie naturală (cum ar fi `key` și `mode`).
""")

#fara old main
#commit nou
#comit norocos- v2