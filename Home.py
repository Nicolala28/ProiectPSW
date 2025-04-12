import streamlit as st

st.set_page_config(page_title="Spotify 2023", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1DB954;'>Top Spotify Songs 2023</h1>", unsafe_allow_html=True)

# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     st.image("data/spotify-logo.png", width=400)
#     st.markdown("### 👨‍🎓 Proiect realizat de studenți")

st.markdown("""
<div style="text-align: center;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg" width="400">
</div>
""", unsafe_allow_html=True)

st.markdown("## 🎯 Motivație și scopul proiectului")
st.markdown("""
Acest proiect are ca scop analiza dataset-ului cu cele mai populare piese de pe **Spotify în 2023**. Alegerea acestei teme este justificată prin:
- **popularitatea globală a platformei Spotify**, cu peste 550 milioane utilizatori lunar;
- **volumul mare de date**, ideal pentru exerciții de procesare, vizualizare și modelare;
- **relevanța practică**: datele sunt reale și permit aplicarea unor tehnici moderne de analiză.

📊 Prin acest proiect, dorim să:
- identificăm **tendințele muzicale actuale**;
- tratăm valori lipsă și outlieri;
- aplicăm tehnici de **preprocesare, encoding și scalare**;
- utilizăm metode de **regresie, clusterizare și analiză statistică**.
""")

st.markdown("<br>", unsafe_allow_html=True)  # două rânduri libere
st.markdown("## 👩‍💻 Autori proiect")

st.markdown("""
- **Iordan Nicola - Diana** – Informatică Economică, anul 3  
- **Jucălea Ioana - Alexia** – Informatică Economică, anul 3
""")


# Sidebar custom
with st.sidebar:
    st.title("📁 Navigare")
    st.markdown("Selectează o pagină din meniu pentru a începe.")

