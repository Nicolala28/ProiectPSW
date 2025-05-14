import streamlit as st
import pandas as pd

st.set_page_config(page_title="Prelucrări Statistice", layout="wide")
st.title("Prelucrări statistice și funcții de grup")

# Încarcă datele deja scalate
df = pd.read_csv("data/data_with_encoding.csv")

# Identificăm coloanele categorice și numerice
categorical_cols = df.select_dtypes(include='object').columns.tolist()
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

st.subheader("1. Grupare pe bază de o variabilă categorică")

selected_cat = st.selectbox("Alege o variabilă categorică pentru grupare:", categorical_cols)

# Selectăm mai multe variabile numerice pentru agregare
selected_nums = st.multiselect(
    "Selectează variabile numerice pentru agregare:",
    numeric_cols,
    default=numeric_cols[:3]
)

# Alegem funcțiile de agregare
agg_funcs = st.multiselect(
    "Alege funcțiile de agregare:",
    ['mean', 'std', 'min', 'max', 'median', 'count'],
    default=['mean', 'std']
)

if selected_cat and selected_nums and agg_funcs:
    grouped_df = df.groupby(selected_cat)[selected_nums].agg(agg_funcs)
    st.subheader("2. Rezultatele agregării")
    st.dataframe(grouped_df, use_container_width=True)

    csv = grouped_df.reset_index().to_csv(index=False).encode('utf-8')
    st.download_button("Descarcă tabelul agregat CSV", csv, file_name="grupare_statistica.csv")
else:
    st.info("Selectează cel puțin o variabilă numerică și o funcție de agregare.")
