import streamlit as st
import pandas as pd
import plotly.express as px


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