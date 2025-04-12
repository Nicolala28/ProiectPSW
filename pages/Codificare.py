import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import LabelEncoder

st.title("Tratarea valorilor lipsă și a outlierilor")

df = pd.read_csv("data/spotify-2023-updated.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.strip()


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