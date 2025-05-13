from operator import index

import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata


st.set_page_config(page_title="Enconding", layout="wide")
st.title("Encodarea variabilelor")


df = pd.read_csv("data/data_with_country_list.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.strip()

# 5. Analiza distribuției datelor pentru variabilele categorice
st.subheader("Analiza distribuției datelor pentru variabilele categorice")

categorical_cols = [col for col in df.select_dtypes(include=['object']).columns if col != 'track_name']

for col in categorical_cols:
    plt.figure(figsize=(8, 4))
    unique_count = df[col].nunique()

    if unique_count > 10:
        top_categories = df[col].value_counts().nlargest(10)
        sns.barplot(x=top_categories.index, y=top_categories.values, palette='viridis')
        plt.title(f"Top 10 valori pentru {col}")
        plt.xlabel(col)
        plt.ylabel("Frecvență")
        plt.xticks(rotation=45)
    else:
        sns.countplot(x=col, data=df, palette='viridis')
        plt.title(f'Distribuția: {col}')
        plt.xlabel(col)
        plt.ylabel('Frecvență')
        plt.xticks(rotation=45)

    plt.tight_layout()
    st.pyplot(plt)

for col in categorical_cols:
    st.write(f"Numărul de instanțe pentru fiecare categorie din `{col}`:")
    value_counts = df[col].value_counts()
    value_counts_df = value_counts.reset_index()
    value_counts_df.columns = [col, 'Frecvență']
    st.write(value_counts_df)


le = LabelEncoder()

# Aplicăm Label Encoding pentru 'key'
df['key_encoded'] = le.fit_transform(df['key'])

# Aplicăm Label Encoding pentru 'mode'
df['mode_encoded'] = le.fit_transform(df['mode'])

# Vizualizăm rezultatele pentru Key și Mode
st.subheader("Label Encoding pentru Key și Mode")
st.write("Datele originale și cele encodate pentru Key și Mode:")
st.dataframe(df[['key', 'key_encoded', 'mode', 'mode_encoded']], use_container_width=True)

# --- Aplicăm Frequency Encoding pentru variabila 'genre' ---
# Calculăm frecvența fiecărui gen
genre_freq = df['genre'].value_counts(normalize=True)

# Aplicăm Frequency Encoding pe 'genre'
df['genre_freq_encoded'] = df['genre'].map(genre_freq)

unique_genres = df[['genre', 'genre_freq_encoded']].drop_duplicates().reset_index(drop=True)

# Afișează doar valorile unice și frecvențele lor
st.subheader("Frequency Encoding pentru Genre")
st.write("Frecvența encodată pentru fiecare gen:")
st.dataframe(unique_genres, use_container_width=True)

# --- Vizualizare distribuiție pentru variabila genre_freq_encoded ---
st.subheader("Distribuția Frequency Encoding pentru Genre")
plt.figure(figsize=(8, 4))
sns.histplot(df['genre_freq_encoded'], bins=20, kde=True, color='purple')
plt.title('Distribuția Frequency Encoding pentru Genre')
plt.xlabel('Frecvența Encodată')
plt.ylabel('Număr de Instanțe')
st.pyplot(plt)

# Calculăm frecvența pentru fiecare combinație de țări
country_freq = df['country_list'].value_counts(normalize=True)

# Aplicăm Frequency Encoding pe country_list
df['country_list_encoded'] = df['country_list'].map(country_freq)
unique_countries = df[['country_list', 'country_list_encoded']].drop_duplicates().reset_index(drop=True)


# Vizualizăm rezultatele pentru Country
st.subheader("Frequency Encoding pentru Country List")
st.write("Frecvența encodată pentru fiecare country:")
st.dataframe(unique_countries, use_container_width=True)

# --- Vizualizare distribuiție pentru variabila country_list_encoded ---
st.subheader("Distribuția Frequency Encoding pentru Country")
plt.figure(figsize=(8, 4))
sns.histplot(df['country_list_encoded'], bins=20, kde=True, color='purple')
plt.title('Distribuția Frequency Encoding pentru Country')
plt.xlabel('Frecvența Encodată')
plt.ylabel('Număr de Instanțe')
st.pyplot(plt)

#ama daugat fisierele noi in github

df.to_csv("data/data_with_encoding.csv", index=False)
